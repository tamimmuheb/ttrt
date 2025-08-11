FROM public.ecr.aws/lambda/python:3.11

# System updates (kept minimal)
RUN python -m pip install --upgrade pip

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src ./src

# Set the CMD to your handler (could be overwritten by AWS Lambda config)
CMD ["src.handlers.pipeline.handler"]