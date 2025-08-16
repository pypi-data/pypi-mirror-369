import requests
import re
import json
import time
from concurrent.futures import ThreadPoolExecutor  # Added for threading
from openai import OpenAI
from mistralai import Mistral
import anthropic
import uuid
import urllib.parse

executor = ThreadPoolExecutor(max_workers=2)  # You can adjust the number of workers
# PricingCache class (outside of Frosty)

# --- Custom Exceptions ---

class FrostyAuthError(Exception):
    """Raised when API key or App ID is invalid."""
    pass

class FrostyRateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    pass

class FrostyProviderError(Exception):
    """Raised when provider returns an unexpected error."""
    pass

class FrostyConfigError(Exception):
    """Raised when SDK setup/config is incomplete or incorrect."""
    pass
class Frosty:
    def __init__(self, router_id, router_key):
        self.router_key = router_key
        self.router_id = router_id
        self.api_base_url = 'https://d7gn6wt7e8.execute-api.us-east-1.amazonaws.com/dev'
        self.api_bedrock_url = 'https://qdza3y79d6.execute-api.us-east-1.amazonaws.com/dev/meta_bedrock'
        self.api_log_base_url = 'https://me0tvn5c73.execute-api.us-east-1.amazonaws.com/dev/log_usage'
        self.api_get_logs_base_url = 'https://jqs5bb2j3a.execute-api.us-east-1.amazonaws.com/dev/get_logs_sdk'
        self.api_store_aggregate_metrics_base_url = 'https://ei4u26nk5c.execute-api.us-east-1.amazonaws.com/dev/store_aggregate_metrics'
        self.api_get_aggregate_metrics_base_url = 'https://iaqyx7i154.execute-api.us-east-1.amazonaws.com/dev/get_aggregate_metrics'
        self.api_get_available_providers_base_url = 'https://w9qrfixtb7.execute-api.us-east-1.amazonaws.com/dev/get_available_providers_sdk'

        # Initialize attributes to store information obtained during connection
        # textGen - primary
        self.text_generation_provider_id = None
        self.text_generation_provider_source = None
        self.text_generation_provider_source_key = None
        self.text_generation_model = None
        
        # textGen - backup
        self.backup_text_generation_provider_id = None
        self.backup_text_generation_provider_source = None
        self.backup_text_generation_provider_source_key = None
        self.backup_text_generation_model = None
        
        # embedding - primary
        self.embedding_provider_id = None
        self.embedding_provider_source = None
        self.embedding_provider_source_key = None
        self.embedding_model = None

        # embedding - backup
        self.backup_embedding_provider_id = None
        self.backup_embedding_provider_source = None
        self.backup_embedding_provider_source_key = None
        self.backup_embedding_model = None
        
        # cost and performance providers for text generation
        self.cost_text_generation_provider_source = None
        self.cost_text_generation_provider_key = None
        self.cost_text_generation_model = None
        
        self.performance_text_generation_provider_source = None
        self.performance_text_generation_provider_key = None
        self.performance_text_generation_model = None

        # cost and performance providers for embeddings
        self.cost_embedding_provider_source = None
        self.cost_embedding_provider_key = None
        self.cost_embedding_model = None
        
        self.performance_embedding_provider_source = None
        self.performance_embedding_provider_key = None
        self.performance_embedding_model = None
        
        self.rule = None
        self.auto_route = False

        # Automatically connect during object creation
        self.connect()

    def connect(self):
        try:
            url = f"https://d7gn6wt7e8.execute-api.us-east-1.amazonaws.com/dev/authorize_connection?app_id={self.router_id}&app_key={self.router_key}"
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "*/*",
            }

            response = self._safe_api_call(url, headers)

            if response and response.status_code == 200:
                cleaned_response_text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', response.text)
                response_data = json.loads(cleaned_response_text)
                
                # textgen
                self.text_generation_provider_id = response_data.get('text_generation_provider_id')
                self.text_generation_provider_source = response_data.get('application_provider_source')
                self.text_generation_provider_source_key = response_data.get('application_provider_source_key')
                self.text_generation_model = response_data.get('text_generation_model')
                
                # textgen backup
                self.backup_text_generation_provider_source = response_data.get('backup_application_provider_source')
                self.backup_text_generation_provider_source_key = response_data.get('backup_application_provider_source_key')
                self.backup_text_generation_model = response_data.get('backup_text_generation_model')

                # embedding
                self.embedding_provider_id = response_data.get('embedding_provider_id')
                self.embedding_provider_source = response_data.get('embedding_provider_source')
                self.embedding_provider_source_key = response_data.get('embedding_provider_source_key')
                self.embedding_model = response_data.get('embedding_model')

                # embedding backup
                self.backup_embedding_provider_source = response_data.get('backup_embedding_provider_source')
                self.backup_embedding_provider_source_key = response_data.get('backup_embedding_provider_source_key')
                self.backup_embedding_model = response_data.get('backup_embedding_model')
                
                # cost and performance models for text generation
                self.cost_text_generation_provider_source = response_data.get('cost_text_generation_provider_source')
                self.cost_text_generation_provider_key = response_data.get('cost_text_generation_provider_key')
                self.cost_text_generation_model = response_data.get('cost_text_generation_provider_model')

                self.performance_text_generation_provider_source = response_data.get('performance_text_generation_provider_source')
                self.performance_text_generation_provider_key = response_data.get('performance_text_generation_provider_key')
                self.performance_text_generation_model = response_data.get('performance_text_generation_provider_model')

                # cost and performance models for embeddings
                self.cost_embedding_provider_source = response_data.get('cost_embedding_provider_source')
                self.cost_embedding_provider_key = response_data.get('cost_embedding_provider_key')
                self.cost_embedding_model = response_data.get('cost_embedding_model')

                self.performance_embedding_provider_source = response_data.get('performance_embedding_provider_source')
                self.performance_embedding_provider_key = response_data.get('performance_embedding_provider_key')
                self.performance_embedding_model = response_data.get('performance_embedding_model')
                
                self.auto_route = response_data.get('auto_route')
                self.success_weight = response_data.get('success_weight')
                self.cost_weight = response_data.get('cost_weight')
                self.latency_weight = response_data.get('latency_weight')
            elif response.status_code == 401:
                raise FrostyAuthError(f"Unauthorized: Invalid app_id or app_key. {response.text}")
            elif response.status_code == 403:
                raise FrostyAuthError(f"Forbidden: Trial expired or access denied. {response.text}")
            elif response.status_code == 429:
                raise FrostyRateLimitError(f"Rate limit exceeded. {response.text}")
            else:
                raise FrostyProviderError(f"Unhandled error ({response.status_code}): {response.text}")

        except requests.exceptions.RequestException as e:
            raise FrostyProviderError(f"Network error connecting to Frosty: {e}")

    def _safe_api_call(self, url, headers, max_retries=1, backoff=0.1, timeout=10):
        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(url, headers=headers, timeout=timeout)
                if response.status_code == 200:
                    return response
                elif response.status_code == 401:
                    raise FrostyAuthError(response.text)
                elif response.status_code == 403:
                    raise FrostyAuthError(response.text)
                elif response.status_code == 429:
                    raise FrostyRateLimitError(response.text)
                else:
                    print(f"API returned error {response.status_code}: {response.text}")
                    raise FrostyProviderError(f"API error {response.status_code}: {response.text}")

            except requests.Timeout:
                print(f"Request timed out, retrying... ({retries + 1}/{max_retries})")
            except requests.RequestException as e:
                print(f"Request failed, retrying: {e}")
            retries += 1
            time.sleep(min(backoff * (2 ** retries), 5))

        raise FrostyProviderError(f"API call failed after {max_retries} attempts")


    def _set_best_model(self):
        query = f"router_id={self.router_id}&router_key={self.router_key}" \
            f"&latency_weight={self.latency_weight if self.latency_weight is not None else 100}" \
            f"&cost_weight={self.cost_weight if self.cost_weight is not None else 100}" \
            f"&success_weight={self.success_weight if self.success_weight is not None else 100}"
    
        url = f"https://6fb1imcd84.execute-api.us-east-1.amazonaws.com/dev/set_auto_route_model_sdk?{query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        }
        requests.get(url, headers=headers)
        
    def chat_fallback(self, prompt, trace_id=None, wait_for_log=True):
        if not self.backup_text_generation_provider_source:
            return {
                'trace_id': uuid.uuid4(),
                'total_tokens': 0,
                'prompt_type': 'chat',
                'prompt_tokens': 0,
                'response_tokens': 0,
                'model': 'None',
                'provider': 'None',
                'total_time': 0,
                'prompt': str(prompt),
                'cost': '- -',
                'rule': self.rule or '- -',
                'response': 'No fallback provider configured',
                'success': 'False'
            }
    
        fallback_provider = self.backup_text_generation_provider_source
        provider_key = self.backup_text_generation_provider_source_key
        model = self.backup_text_generation_model
        print(f"Attempting fallback with: {fallback_provider}, model: {model}")
        if fallback_provider == 'OpenAI':
            return self.openai_chat(prompt, provider_key, model, trace_id, fallback=True, wait_for_log=wait_for_log)
        elif fallback_provider == 'MistralAI':
            return self.mistralai_chat(prompt, provider_key, model, trace_id, fallback=True, wait_for_log=wait_for_log)
        elif fallback_provider == 'Anthropic':
            return self.anthropic_chat(prompt, provider_key, model, trace_id, fallback=True, wait_for_log=wait_for_log)
        elif fallback_provider == 'Meta':
            return self.meta_chat(prompt, provider_key, model, trace_id, fallback=True, wait_for_log=wait_for_log)
        else:
              # If no more fallbacks are available, return an error
            return {'statusCode': 500, 'body': 'Fallback provider is not configured'}

    def _choose_best_model(self):
        try:
            query = f"router_id={self.router_id}&router_key={self.router_key}"
            url = f"https://fd5611on9l.execute-api.us-east-1.amazonaws.com/dev/get_auto_route_model_sdk?{query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                response_body = response.text
                
                # Remove extra quotes around the string to make it a valid dictionary string
                response_body = response_body.strip('"').replace("'", '"')
                
                # Convert the string to a dictionary
                response_data = json.loads(response_body)

                # Store sensitive values internally
                self._auto_provider_key = response_data.get('ProviderKey')
                self._auto_application_key = response_data.get('ApplicationKey')
                self._auto_application_id = response_data.get('ApplicationId')

                # Return only the non-sensitive info needed for routing
                return {
                    'ProviderSource': response_data.get('ProviderSource'),
                    'Model': response_data.get('Model')
                }

        except requests.exceptions.RequestException as e:
            print('Error logging data')
            raise ConnectionError(f'Failed to log: {e}.')


    def _merge_context(self, prompt, context):
        """Return messages with context prepended to the first user message.
        Accepts prompt as list[{"role","content"}] or a string."""
        if not context:
            return prompt

        # normalize to messages list
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = list(prompt)  # shallow copy

        # find first user message
        for i, msg in enumerate(messages):
            if msg.get("role") == "user":
                messages[i] = {
                    "role": "user",
                    "content": (
                        f"Use the following information to answer accurately. "
                        f"If the information doesn’t contain the answer, say so.\n\n"
                        f"--- Context Start ---\n{context}\n--- Context End ---\n\n"
                        f"{msg.get('content','')}"
                    ),
                }
                break
        else:
            # no user message found; create one
            messages.insert(0, {
                "role": "user",
                "content": (
                    f"Use the following information to answer accurately.\n\n"
                    f"--- Context Start ---\n{context}\n--- Context End ---"
                ),
            })
        return messages

    def chat(self, prompt, context=None, rule=None, thinking= None, wait_for_log=True):
        if self.auto_route == "true":
            best_model = self._choose_best_model()
            primary_provider = best_model.get('ProviderSource', self.backup_text_generation_provider_source)
            provider_key = self._auto_provider_key or self.backup_text_generation_provider_source_key
            model = best_model.get('Model', self.backup_text_generation_model)
            print(f"Trying with autorouter provider: {primary_provider}, model: {model}")

        else:
            self.rule = rule
            if rule == "cost" and  self.cost_text_generation_provider_source:
                primary_provider = self.cost_text_generation_provider_source
                provider_key=self.cost_text_generation_provider_key
                model=self.cost_text_generation_model
                print(f"Trying with cost provider: {primary_provider}, model: {model}")
            elif rule == "performance" and self.performance_text_generation_provider_source:
                primary_provider = self.performance_text_generation_provider_source
                provider_key=self.performance_text_generation_provider_key
                model=self.performance_text_generation_model
                print(f"Trying with performance provider: {primary_provider}, model: {model}")
            else:
                primary_provider = self.text_generation_provider_source
                provider_key=self.text_generation_provider_source_key
                model=self.text_generation_model
                print(f"Trying with primary provider: {primary_provider}, model: {model}")

        try:
            prompt = self._merge_context(prompt, context)

            if primary_provider == 'OpenAI':
                return self.openai_chat(prompt, provider_key, model, wait_for_log=True)
            elif primary_provider == 'MistralAI':
                return self.mistralai_chat(prompt, provider_key, model, wait_for_log=True)
            elif primary_provider == 'Anthropic':
                return self.anthropic_chat(prompt, provider_key, model, thinking=thinking, wait_for_log=True)
            elif primary_provider == 'Meta':
                return self.meta_chat(prompt, model, wait_for_log=True)
            else:
                raise ConnectionError(f'{primary_provider} is not configured for the Python SDK yet')
        except Exception as e:
            print(f"Primary provider failed: {str(e)}")
            # If the primary provider fails, call the fallback
            return self.chat_fallback(prompt, wait_for_log)

    def openai_chat(self, prompt, api_key, model, trace_id=None, fallback=False, wait_for_log=True):
        trace_id = trace_id if trace_id else uuid.uuid4()
        try:
            client = OpenAI(api_key=api_key)
            start_time = time.time()
            chat_completion = client.chat.completions.create(
                model=model,
                messages=prompt
            )
            elapsed_time = time.time() - start_time

            log = {
                'trace_id': trace_id,
                'total_tokens': chat_completion.usage.total_tokens,
                'prompt_type': 'chat',
                'prompt_tokens': chat_completion.usage.prompt_tokens,
                'response_tokens': chat_completion.usage.completion_tokens,
                'model': chat_completion.model,
                'provider': 'OpenAI',
                'total_time': round(elapsed_time * 1000, 2),
                'prompt': prompt,
                'cost': '- -',
                'rule': self.rule or '- -',
                'response': str(chat_completion.choices[0].message.content),
                "success": True
            }
            # Run log and _set_best_model in the background
            # ✅ Check flag and decide if log is async or sync
            if wait_for_log:
                self.log(log)  # synchronous
                self._set_best_model()
            else:
                executor.submit(self.log, log)  # async
                executor.submit(self._set_best_model)  # keep async

            return log

        except Exception as e:
            if fallback:
                return {'statusCode': 500, 'body': str(e)} 
            else:
                print(f"Primary provider failed: {str(e)}") 
                log = {
                    'trace_id': trace_id,
                    'total_tokens': 0,
                    'prompt_type': 'chat',
                    'prompt_tokens': 0,
                    'response_tokens': 0,
                    'model': model,
                    'provider': 'OpenAI',
                    'total_time': 0,
                    'prompt': prompt,
                    'cost': '- -',
                    'rule': self.rule or '- -',
                    'response': str(e),
                    'success': 'False'
                }
                # Run log and _set_best_model in the background
                if wait_for_log:
                    self.log(log)  # synchronous
                else:
                    executor.submit(self.log, log)  # async
                return self.chat_fallback(prompt, trace_id, wait_for_log)

    def mistralai_chat(self, prompt, api_key, model, trace_id=None, fallback=False, wait_for_log=True):
        trace_id = trace_id if trace_id else uuid.uuid4()

        try:
            client = Mistral(api_key=api_key)
            start_time = time.time()
            messages = [{"role": msg["role"], "content": msg["content"]} for msg in prompt]

            chat_response = client.chat.complete(model=model, messages=messages)
            elapsed_time = time.time() - start_time
            
            log = {
                'trace_id': trace_id,
                'total_tokens': chat_response.usage.total_tokens if hasattr(chat_response, 'usage') else 0,
                'prompt_type': 'chat',
                'prompt_tokens': chat_response.usage.prompt_tokens if hasattr(chat_response.usage, 'prompt_tokens') else 0,
                'response_tokens': chat_response.usage.completion_tokens if hasattr(chat_response.usage, 'completion_tokens') else 0,
                'model': getattr(chat_response, 'model', 'unknown'),
                'provider': 'MistralAI',
                'total_time': round(elapsed_time * 1000, 2),
                'prompt': str(messages),
                'cost': '- -',
                'rule': self.rule or '- -',
                'response': chat_response.choices[0].message.content if chat_response.choices else '',
                'success': 'True'
            }
            # Run log and _set_best_model in the background
            # Run log and _set_best_model in the background
            # ✅ Check flag and decide if log is async or sync
            if wait_for_log:
                self.log(log)  # synchronous
                self._set_best_model()
            else:
                executor.submit(self.log, log)  # async
                executor.submit(self._set_best_model)  # keep async

            return log

        except Exception as e:
            if fallback:
                return {'statusCode': 500, 'body': str(e)} 
            else:
                print(f"Primary provider failed: {str(e)}") 
                log = {
                    'trace_id': trace_id,
                    'total_tokens': 0,
                    'prompt_type': 'chat',
                    'prompt_tokens': 0,
                    'response_tokens': 0,
                    'model': model,
                    'provider': 'MistralAI',
                    'cost': '- -',
                    'rule': self.rule or '- -',
                    'total_time': 0,
                    'prompt': prompt,
                    'response': str(e),
                    'success': 'False'
                }
                # Run log and _set_best_model in the background
                if wait_for_log:
                    self.log(log)  # synchronous
                else:
                    executor.submit(self.log, log)  # async
                return self.chat_fallback(prompt, trace_id, wait_for_log)

    def anthropic_chat(self, prompt, api_key, model, trace_id=None, fallback=False, thinking=None, wait_for_log=True):
        trace_id = trace_id if trace_id else uuid.uuid4()
        try:
            client = anthropic.Anthropic(api_key=api_key)
            start_time = time.time()
            
            message_params = {
                "model": model,
                "max_tokens": 2000,
                "messages": prompt,
            }

            if thinking is not None and "claude-3-7-sonnet" in model:
                message_params["thinking"] = thinking

            message = client.messages.create(**message_params)
            elapsed_time = time.time() - start_time
            
            # text_block = message.content[0]  # Access the first TextBlock in the content list
            text_block = next((item for item in message.content if getattr(item, "type", None) == "text"), None)

            text_content = text_block.text   # Extract the text attribute
            
            log = {
                'trace_id': trace_id,
                'total_tokens': message.usage.input_tokens + message.usage.output_tokens,
                'prompt_type': 'chat',
                'prompt_tokens': message.usage.input_tokens,
                'response_tokens': message.usage.output_tokens,
                'model': message.model,
                'provider': 'Anthropic',
                'total_time': round(elapsed_time * 1000, 2),
                'prompt': prompt,
                'cost': '- -',
                'rule': self.rule or '- -',
                'response': str(text_content),
                'success': 'True'
            }
            # Run log and _set_best_model in the background
            # ✅ Check flag and decide if log is async or sync
            if wait_for_log:
                self.log(log)  # synchronous
                self._set_best_model()
            else:
                executor.submit(self.log, log)  # async
                executor.submit(self._set_best_model)  # keep async

            return log

        except Exception as e:
            if fallback:
                return {'statusCode': 500, 'body': str(e)} 
            else:
                print(f"Primary provider failed: {str(e)}") 
                log = {
                    'trace_id': trace_id,
                    'total_tokens': 0,
                    'prompt_type': 'chat',
                    'prompt_tokens': 0,
                    'response_tokens': 0,
                    'model': model,
                    'provider': 'Anthropic',
                    'total_time': 0,
                    'prompt': prompt,
                    'cost': '- -',
                    'rule': self.rule or '- -',
                    'response': str(e),
                    'success': 'False'
                }
                # Run log and _set_best_model in the background
                if wait_for_log:
                    self.log(log)  # synchronous
                else:
                    executor.submit(self.log, log)  # async
                return self.chat_fallback(prompt, trace_id, wait_for_log)

    def meta_chat(self, prompt, model, trace_id=None, fallback=False, wait_for_log=True):
        trace_id = trace_id if trace_id else uuid.uuid4()

        query = f"app_id={self.router_id}&app_key={self.router_key}&model={model}&prompt={prompt[0]['content']}"
        try:
            url = f"{self.api_bedrock_url}?{query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            }
            start_time = time.time()

            response = self._safe_api_call(url, headers)

            elapsed_time = time.time() - start_time

            if response and response.status_code == 200:
                response_data = json.loads(response.text)
                log = {
                    'trace_id': trace_id,
                    'total_tokens': response_data['prompt_token_count'] + response_data['generation_token_count'],
                    'prompt_type': 'chat',
                    'prompt_tokens': response_data['prompt_token_count'],
                    'response_tokens': response_data['generation_token_count'],
                    'model': self.text_generation_model,
                    'provider': 'Meta',
                    'total_time': round(elapsed_time * 1000, 2),
                    'prompt': str(prompt[0]["content"]),
                    'cost': '- -',
                    'rule': self.rule or '- -',
                    'response': response_data['generation'],
                    'success': 'True'
                }
                # Run log and _set_best_model in the background
                # ✅ Check flag and decide if log is async or sync
                if wait_for_log:
                    self.log(log)  # synchronous
                    self._set_best_model()
                else:
                    executor.submit(self.log, log)  # async
                    executor.submit(self._set_best_model)  # keep async

                return log
            
        except requests.Timeout as e:
            print(f"Meta provider timed out: {str(e)}")
            log = {
                'trace_id': trace_id,
                'total_tokens': 0,
                'prompt_type': 'chat',
                'prompt_tokens': 0,
                'response_tokens': 0,
                'model': model,
                'provider': 'Meta',
                'total_time': 0,
                'prompt': prompt,
                'cost': '- -',
                'rule': self.rule or '- -',
                'response': str(e),
                'success': 'False'
            }
            # Run log and _set_best_model in the background
            if wait_for_log:
                self.log(log)  # synchronous
            else:
                executor.submit(self.log, log)  # async
            return {'statusCode': 500, 'body': 'Meta provider timeout'} if fallback else self.chat_fallback(prompt, trace_id, wait_for_log)
        
        except requests.exceptions.RequestException as e:
            print(f"Exception in meta_chat: {str(e)}")
            log = {
                'trace_id': trace_id,
                'total_tokens': 0,
                'prompt_type': 'chat',
                'prompt_tokens': 0,
                'response_tokens': 0,
                'model': model,
                'provider': 'Meta',
                'total_time': 0,
                'prompt': prompt,
                'cost': '- -',
                'rule': self.rule or '- -',
                'response': str(e),
                'success': 'False'
            }
            # Run log and _set_best_model in the background
            if wait_for_log:
                self.log(log)  # synchronous
            else:
                executor.submit(self.log, log)  # async
            return {'statusCode': 500, 'body': str(e)} if fallback else self.chat_fallback(prompt, trace_id, wait_for_log)

        except Exception as e:
            print(f"Exception in meta_chat: {str(e)}")
            log = {
                'trace_id': trace_id,
                'total_tokens': 0,
                'prompt_type': 'chat',
                'prompt_tokens': 0,
                'response_tokens': 0,
                'model': model,
                'provider': 'Meta',
                'total_time': 0,
                'cost': '- -',
                'rule': self.rule or '- -',
                'prompt': prompt,
                'response': str(e),
                'success': 'False'
            }
            # Run log and _set_best_model in the background
            if wait_for_log:
                self.log(log)  # synchronous
            else:
                executor.submit(self.log, log)  # async
            return {'statusCode': 500, 'body': str(e)} if fallback else self.chat_fallback(prompt, trace_id,wait_for_log)


    def embedding_fallback(self, prompt, trace_id = None, wait_for_log=True):

        if not self.backup_embedding_provider_source:
            return {
                'trace_id': uuid.uuid4(),
                'total_tokens': 0,
                'prompt_type': 'embeddings',
                'prompt_tokens': 0,
                'response_tokens': 0,
                'model': 'None',
                'provider': 'None',
                'total_time': 0,
                'prompt': str(prompt),
                'cost': '- -',
                'rule': self.rule or '- -',
                'response': 'No fallback provider configured',
                'success': 'False'
            }
        fallback_provider = self.backup_embedding_provider_source
        provider_key = self.backup_embedding_provider_source_key
        model = self.backup_embedding_model

        print(f"Attempting fallback with: {fallback_provider}, model: {model}")
        if fallback_provider == 'OpenAI':
            return self.openai_embeddings(prompt, provider_key, model, trace_id, fallback=True, wait_for_log=wait_for_log)
        elif fallback_provider == 'MistralAI':
            return self.mistralai_embeddings(prompt, provider_key, model, trace_id, fallback=True, wait_for_log=wait_for_log)
        else:
            return {'statusCode': 500, 'body': 'Fallback provider is not configured'}    
        
    def embeddings(self, prompt, rule=None, wait_for_log=True):
        self.rule = rule
        if rule == "cost" and self.cost_embedding_provider_source:
            primary_provider = self.cost_embedding_provider_source
            provider_key=self.cost_embedding_provider_key
            model=self.cost_embedding_model
            print(f"Trying with cost provider: {primary_provider}, model: {model}")
        elif rule == "performance" and self.performance_embedding_provider_source:
            primary_provider = self.performance_embedding_provider_source
            provider_key=self.performance_embedding_provider_key
            model=self.performance_embedding_model
            print(f"Trying with performance provider: {primary_provider}, model: {model}")
        else:
            primary_provider = self.embedding_provider_source
            provider_key=self.embedding_provider_source_key
            model=self.embedding_model
            print(f"Trying with primary provider: {primary_provider}, model: {model}")

        if not primary_provider or not provider_key or not model:
            return {
                'trace_id': uuid.uuid4(),
                'total_tokens': 0,
                'prompt_type': 'embeddings',
                'prompt_tokens': 0,
                'response_tokens': 0,
                'model': 'None',
                'provider': 'None',
                'total_time': 0,
                'prompt': str(prompt),
                'cost': '- -',
                'rule': self.rule or '- -',
                'response': 'No valid provider configured',
                'success': 'False'
            }
        # Try with the primary provider
        try:
            if primary_provider == 'OpenAI':
                return self.openai_embeddings(prompt, provider_key, model, wait_for_log)
            elif primary_provider == 'MistralAI':
                return self.mistralai_embeddings(prompt, provider_key, model, wait_for_log)
            else:
                raise ConnectionError(f'{primary_provider} is not configured for the Python SDK yet')

        except Exception as e:
            print(f"Primary provider failed: {str(e)}")
            # If the primary provider fails, call the fallback
            return self.embedding_fallback(prompt, wait_for_log=wait_for_log)

    def openai_embeddings(self, prompt, api_key, model, trace_id=None, fallback=False, wait_for_log=True):
        trace_id = trace_id if trace_id else uuid.uuid4()

        client = OpenAI(api_key=api_key)
        submitted_prompt = prompt[0] if isinstance(prompt, list) and len(prompt) > 0 else prompt
        try:
            start_time = time.time() 
            response = client.embeddings.create(
                input = submitted_prompt,
                model=model
            )
            end_time = time.time() 
            elapsed_time = end_time - start_time

            log = {
                'trace_id': trace_id,
                'total_tokens': response.usage.total_tokens,
                'prompt_type':'embeddings',
                'prompt_tokens': response.usage.prompt_tokens,
                'response_tokens': (response.usage.total_tokens - response.usage.prompt_tokens),
                'model':response.model,
                'provider':'OpenAI',
                'total_time': round(elapsed_time * 1000, 2),  # Convert to milliseconds and round to two decimal places
                'cost': '- -',
                'rule': self.rule or '- -',
                'prompt': str(submitted_prompt),
                'response': '--',
                'success': 'True'
            }
            
            # Run log and _set_best_model in the background
            executor.submit(self.log, log)          # Logging happens in the background

            log['response'] =str(response.data[0].embedding)
            return log
            
        except Exception as e:
            if fallback:
                log = {
                    'trace_id': trace_id,
                    'total_tokens': 0,
                    'prompt_type': 'embeddings',
                    'prompt_tokens': 0,
                    'response_tokens': 0,
                    'model': model,
                    'provider': 'OpenAI',
                    'total_time': 0,
                    'cost': '- -',
                    'rule': self.rule or '- -',
                    'prompt': prompt,
                    'response': str(e),
                    'success': 'False'
                }
                # Run log and _set_best_model in the background
                executor.submit(self.log, log)          # Logging happens in the background
                return {'statusCode': 500, 'body': str(e)} 
            else:
                print(f"Primary provider failed: {str(e)}") 
                return self.embedding_fallback(prompt, trace_id, wait_for_log)
        
    def mistralai_embeddings(self, prompt, api_key, model,trace_id=None, fallback=False, wait_for_log=True):
        trace_id = trace_id if trace_id else uuid.uuid4()

        try:
            client = Mistral(api_key=api_key)
            start_time = time.time()

            # Making the embeddings request
            embeddings_batch_response = client.embeddings.create(model=model, inputs=prompt)

            end_time = time.time()
            elapsed_time = end_time - start_time

            # Constructing the log
            log = {
                'trace_id': trace_id,
                'prompt_type': 'embeddings',
                'total_tokens': embeddings_batch_response.usage.total_tokens if hasattr(embeddings_batch_response, 'usage') else 0,
                'prompt_tokens': embeddings_batch_response.usage.prompt_tokens if hasattr(embeddings_batch_response.usage, 'prompt_tokens') else 0,
                'response_tokens': (embeddings_batch_response.usage.total_tokens - embeddings_batch_response.usage.prompt_tokens) if hasattr(embeddings_batch_response, 'usage') else 0,
                'model': getattr(embeddings_batch_response, 'model', 'unknown'),
                'provider': 'MistralAI',
                'total_time': round(elapsed_time * 1000, 2),  # Convert to milliseconds
                'prompt': prompt,
                'cost': '- -',
                'rule': self.rule or '- -',
                'result': str(embeddings_batch_response.data),  # Include the embeddings data in the log if needed
                'success': 'True'
            }

            
            # Run log and _set_best_model in the background
            executor.submit(self.log, log)          # Logging happens in the background

            log['result'] = embeddings_batch_response

            return log
        except Exception as e:
            if fallback:
                return {'statusCode': 500, 'body': str(e)} 
            else:
                print(f"Primary provider failed: {str(e)}") 
                log = {
                    'trace_id': trace_id,
                    'total_tokens': 0,
                    'prompt_type': 'embeddings',
                    'prompt_tokens': 0,
                    'response_tokens': 0,
                    'model': model,
                    'provider': 'MistralAI',
                    'total_time': 0,
                    'cost': '- -',
                    'rule': self.rule or '- -',
                    'prompt': prompt,
                    'response': str(e),
                    'success': 'False'
                }
                # Run log and _set_best_model in the background
                executor.submit(self.log, log)          # Logging happens in the background
                
                return self.embedding_fallback(prompt, trace_id, wait_for_log=wait_for_log)
        
        
    def log(self, log):
        # Ensure the parameters are URL-encoded, especially for prompt and response
        query = f"app_id={self.router_id}&app_key={self.router_key}&total_tokens={log['total_tokens']}&" \
                f"prompt_type={log['prompt_type']}&prompt_tokens={log['prompt_tokens']}&response_tokens={log['response_tokens']}&" \
                f"model={urllib.parse.quote_plus(log['model'])}&cost={log['cost']}&rule={log['rule']}&" \
                f"provider={log['provider']}&total_time={log['total_time']}&prompt={urllib.parse.quote_plus(str(log['prompt']))}&" \
                f"response={urllib.parse.quote_plus(log['response'])}&trace_id={log['trace_id']}&success={log['success']}"

        try:
            url = f"{self.api_log_base_url}?{query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            }
            response = requests.get(url, headers=headers)
            return response and response.status_code == 200
        except requests.exceptions.RequestException as e:
            print('Error logging data')
            raise ConnectionError(f'Failed to log: {e}.')
        
    def __getattribute__(self, name):
        # Block access to sensitive provider keys
        if "_provider_key" in name:
            raise AttributeError(f'Access to `{name}` is restricted for security.')
        return super().__getattribute__(name)

    def __dir__(self):
        # Hide sensitive attributes from dir() and autocompletion
        return [item for item in super().__dir__() if "_provider_key" not in item and not item.startswith("_router_key")]
