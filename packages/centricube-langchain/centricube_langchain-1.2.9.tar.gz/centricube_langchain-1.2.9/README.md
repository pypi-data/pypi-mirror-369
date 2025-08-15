## What is centricube-langchain?

centricube-langchain is an open-source langchain extending library built to power building LLM application.
centricube-langchain provides more components to support Chinese LLMs and and Chinese based token environments for prompt engineering and ICL template.


The project is a sub-module of [centricube](https://github.com/cicit/centricube).


## Key features

- Retrival Enhancement components, like ESIndex, DBIndex, GraphIndex 
- Supporting Open LLMs and embeddings models 
- High performance QAs Chains
- High Semanticly Chinese token processing


## Quick start

### Start with Centricube Platform.

We provide a open cloud service for easily use. See [free trial](https://www.centricube.cn/).

### Install centricube-langchain

- Install from pip: `pip install centricube-langchain`
- [Quick Start Guide](https://scn3v8ba0o9m.feishu.cn/wiki/XTRVw4tUHi4ZQ2kDQpXc0l47nLg)

### Docker Deployment

To deploy via Docker:

1. **Build the image**:
   ```bash
   docker build -t centricube-langchain .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8000:8000 centricube-langchain
   ```

3. **Push to Docker Hub** (optional):
   ```bash
   docker tag centricube-langchain yourusername/centricube-langchain
   docker push yourusername/centricube-langchain
   ```

Replace `yourusername` with your Docker Hub username.

## Documentation

For guidance on installation, development, deployment, and administration, 
check out [centricube-langchain Dev Docs](https://scn3v8ba0o9m.feishu.cn/wiki/XTRVw4tUHi4ZQ2kDQpXc0l47nLg). 


## Acknowledgments

centricube-langchain adopts dependencies from the following:

- Thanks to [langchain](https://github.com/langchain-ai/langchain) for the main framework.
