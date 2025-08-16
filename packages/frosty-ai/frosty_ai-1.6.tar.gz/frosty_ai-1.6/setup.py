from setuptools import setup

setup(
    name='frosty_ai',
    version='1.06',  # Update the version as needed
    packages=['frosty_ai'],
    install_requires=[
        'requests',
        'openai>=0.28.0',
        'mistralai>=1.5.0',  # Latest confirmed that uses pydantic >= 2.8.2
        'anthropic>=0.49.0',
        # 'pydantic>=2.8.2',  # ✅ Add this to make explicit
        'urllib3<1.27,>=1.25.4',  # To avoid breaking botocore dependencies if AWS SDK used
        # Add other dependencies as needed
    ],
    author='FrostyAI',
    author_email='brittany@gofrosty.ai',
    description='A Python package for seamless multi-LLM routing, observability, and LLM-agnostic integration.',
    long_description="""
        Frosty AI is a Python package for seamless multi-LLM (Large Language Model) routing, observability, and management.
        
        Frosty empowers developers and organizations to remain LLM-agnostic, enabling seamless integration, management, and switching between various LLM providers without vendor lock-in. 
        With Frosty, you can:
        
        - Flexibly integrate with multiple LLM providers like OpenAI, Anthropic, and Mistral.
        - Future-proof your applications by easily switching to new or better-performing models as they become available.
        - Optimize costs by choosing models based on performance and pricing, avoiding vendor lock-in.
        
        For the most up-to-date documentation and usage examples, please visit the [Frosty AI Documentation](https://docs.gofrosty.ai/frosty-ai-docs/frosty-ai-documentation).
    """,
    long_description_content_type='text/markdown',
    url='https://docs.gofrosty.ai/frosty-ai-docs/frosty-ai-documentation',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
