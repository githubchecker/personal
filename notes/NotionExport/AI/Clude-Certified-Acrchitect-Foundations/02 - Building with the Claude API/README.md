# ⚡ Course 02 — Building with the Claude API

> [← Prev Course: 01 - AI Fluency](../01%20-%20AI%20Fluency%20-%20Framework%20and%20Foundations/README.md) · [Master Syllabus](../README.md) · [Next Course: 03 - Claude on Google Cloud →](../03%20-%20Claude%20on%20Google%20Cloud/README.md)

This comprehensive course covers the practical software engineering and enterprise architecture of building with Anthropic's foundation models via the **Claude API**. Topics include model families, API authentication, multi-turn state management, system prompts, structured JSON outputs, response streaming, prompt evaluation suites, tool use & function calling, Retrieval-Augmented Generation (RAG), advanced features (Extended Thinking, Prompt Caching, Citations, Vision, PDF support), Model Context Protocol (MCP), Claude Code, and agentic workflow patterns.

---

## 📋 Course Curriculum & Lesson Index

### 1. Introduction
- [x] **01** · [Welcome to the course](01%20-%20Introduction/01%20Welcome%20to%20the%20course.md)

### 2. Anthropic Overview
- [x] **02** · [Overview of Claude models](02%20-%20Anthropic%20overview/01%20Overview%20of%20Claude%20models.md)

### 3. Accessing Claude with the API
- [x] **03** · [Accessing the API](03%20-%20Accessing%20Claude%20with%20the%20API/01%20Accessing%20the%20API.md)
- [x] **04** · [Getting an API key](03%20-%20Accessing%20Claude%20with%20the%20API/02%20Getting%20an%20API%20key.md)
- [x] **05** · [Making a request](03%20-%20Accessing%20Claude%20with%20the%20API/03%20Making%20a%20request.md)
- [x] **06** · [Multi-Turn conversations](03%20-%20Accessing%20Claude%20with%20the%20API/04%20Multi-Turn%20conversations.md)
- [x] **07** · [Chat exercise](03%20-%20Accessing%20Claude%20with%20the%20API/05%20Chat%20exercise.md)
- [x] **08** · [System prompts](03%20-%20Accessing%20Claude%20with%20the%20API/06%20System%20prompts.md)
- [x] **09** · [System prompts exercise](03%20-%20Accessing%20Claude%20with%20the%20API/07%20System%20prompts%20exercise.md)
- [x] **10** · [Temperature](03%20-%20Accessing%20Claude%20with%20the%20API/08%20Temperature.md)
- [x] **11** · [Response streaming](03%20-%20Accessing%20Claude%20with%20the%20API/09%20Response%20streaming.md)
- [x] **12** · [Structured data](03%20-%20Accessing%20Claude%20with%20the%20API/10%20Structured%20data.md)

### 4. Prompt Evaluation
- [x] **13** · [Prompt evaluation](04%20-%20Prompt%20evaluation/01%20Prompt%20evaluation.md)
- [x] **14** · [A typical eval workflow](04%20-%20Prompt%20evaluation/02%20A%20typical%20eval%20workflow.md)
- [x] **15** · [Generating test datasets](04%20-%20Prompt%20evaluation/03%20Generating%20test%20datasets.md)
- [x] **16** · [Running the eval](04%20-%20Prompt%20evaluation/04%20Running%20the%20eval.md)
- [x] **17** · [Model based grading](04%20-%20Prompt%20evaluation/05%20Model%20based%20grading.md)
- [x] **18** · [Code based grading](04%20-%20Prompt%20evaluation/06%20Code%20based%20grading.md)

### 5. Prompt Engineering Techniques
- [ ] **19** · [Prompt engineering](05%20-%20Prompt%20engineering%20techniques/01%20Prompt%20engineering.md)
- [ ] **20** · [Being clear and direct](05%20-%20Prompt%20engineering%20techniques/02%20Being%20clear%20and%20direct.md)
- [ ] **21** · [Being specific](05%20-%20Prompt%20engineering%20techniques/03%20Being%20specific.md)
- [ ] **22** · [Structure with XML tags](05%20-%20Prompt%20engineering%20techniques/04%20Structure%20with%20XML%20tags.md)
- [ ] **23** · [Providing examples](05%20-%20Prompt%20engineering%20techniques/05%20Providing%20examples.md)
- [ ] **24** · [Exercise on prompting](05%20-%20Prompt%20engineering%20techniques/06%20Exercise%20on%20prompt%20prompting.md)
- [ ] **25** · [Quiz on prompt engineering techniques](05%20-%20Prompt%20engineering%20techniques/07%20Quiz%20on%20prompt%20engineering%20techniques.md)

### 6. Tool Use with Claude
- [ ] **26** · [Introducing tool use](06%20-%20Tool%20use%20with%20Claude/01%20Introducing%20tool%20use.md)
- [ ] **27** · [Project overview](06%20-%20Tool%20use%20with%20Claude/02%20Project%20overview.md)
- [ ] **28** · [Tool functions](06%20-%20Tool%20use%20with%20Claude/03%20Tool%20functions.md)
- [ ] **29** · [Tool schemas](06%20-%20Tool%20use%20with%20Claude/04%20Tool%20schemas.md)
- [ ] **30** · [Handling message blocks](06%20-%20Tool%20use%20with%20Claude/05%20Handling%20message%20blocks.md)
- [ ] **31** · [Sending tool results](06%20-%20Tool%20use%20with%20Claude/06%20Sending%20tool%20results.md)
- [ ] **32** · [Multi-turn conversations with tools](06%20-%20Tool%20use%20with%20Claude/07%20Multi-turn%20conversations%20with%20tools.md)
- [ ] **33** · [Implementing multiple turns](06%20-%20Tool%20use%20with%20Claude/08%20Implementing%20multiple%20turns.md)
- [ ] **34** · [Using multiple tools](06%20-%20Tool%20use%20with%20Claude/09%20Using%20multiple%20tools.md)
- [ ] **35** · [Fine grained tool calling](06%20-%20Tool%20use%20with%20Claude/10%20Fine%20grained%20tool%20calling.md)
- [ ] **36** · [The text edit tool](06%20-%20Tool%20use%20with%20Claude/11%20The%20text%20edit%20tool.md)
- [ ] **37** · [The web search tool](06%20-%20Tool%20use%20with%20Claude/12%20The%20web%20search%20tool.md)
- [ ] **38** · [Quiz on tool use with Claude](06%20-%20Tool%20use%20with%20Claude/13%20Quiz%20on%20tool%20use%20with%20Claude.md)

### 7. RAG and Agentic Search
- [ ] **39** · [Introducing Retrieval Augmented Generation](07%20-%20RAG%20and%20Agentic%20Search/01%20Introducing%20Retrieval%20Augmented%20Generation.md)
- [ ] **40** · [Text chunking strategies](07%20-%20RAG%20and%20Agentic%20Search/02%20Text%20chunking%20strategies.md)
- [ ] **41** · [Text embeddings](07%20-%20RAG%20and%20Agentic%20Search/03%20Text%20embeddings.md)
- [ ] **42** · [The full RAG flow](07%20-%20RAG%20and%20Agentic%20Search/04%20The%20full%20RAG%20flow.md)
- [ ] **43** · [Implementing the RAG flow](07%20-%20RAG%20and%20Agentic%20Search/05%20Implementing%20the%20RAG%20flow.md)
- [ ] **44** · [BM25 lexical search](07%20-%20RAG%20and%20Agentic%20Search/06%20BM25%20lexical%20search.md)
- [ ] **45** · [A Multi-Index RAG pipeline](07%20-%20RAG%20and%20Agentic%20Search/07%20A%20Multi-Index%20RAG%20pipeline.md)

### 8. Features of Claude
- [ ] **46** · [Extended thinking](08%20-%20Features%20of%20Claude/01%20Extended%20thinking.md)
- [ ] **47** · [Image support](08%20-%20Features%20of%20Claude/02%20Image%20support.md)
- [ ] **48** · [PDF support](08%20-%20Features%20of%20Claude/03%20PDF%20support.md)
- [ ] **49** · [Citations](08%20-%20Features%20of%20Claude/04%20Citations.md)
- [ ] **50** · [Prompt caching](08%20-%20Features%20of%20Claude/05%20Prompt%20caching.md)
- [ ] **51** · [Rules of prompt caching](08%20-%20Features%20of%20Claude/06%20Rules%20of%20prompt%20caching.md)
- [ ] **52** · [Prompt caching in action](08%20-%20Features%20of%20Claude/07%20Prompt%20caching%20in%20action.md)
- [ ] **53** · [Code execution and the Files API](08%20-%20Features%20of%20Claude/08%20Code%20execution%20and%20the%20Files%20API.md)
- [ ] **54** · [Quiz on features of Claude](08%20-%20Features%20of%20Claude/09%20Quiz%20on%20features%20of%20Claude.md)

### 9. Model Context Protocol
- [ ] **55** · [Introducing MCP](09%20-%20Model%20Context%20Protocol/01%20Introducing%20MCP.md)
- [ ] **56** · [MCP clients](09%20-%20Model%20Context%20Protocol/02%20MCP%20clients.md)
- [ ] **57** · [Project setup](09%20-%20Model%20Context%20Protocol/03%20Project%20setup.md)
- [ ] **58** · [Defining tools with MCP](09%20-%20Model%20Context%20Protocol/04%20Defining%20tools%20with%20MCP.md)
- [ ] **59** · [The server inspector](09%20-%20Model%20Context%20Protocol/05%20The%20server%20inspector.md)
- [ ] **60** · [Implementing a client](09%20-%20Model%20Context%20Protocol/06%20Implementing%20a%20client.md)
- [ ] **61** · [Defining resources](09%20-%20Model%20Context%20Protocol/07%20Defining%20resources.md)
- [ ] **62** · [Accessing resources](09%20-%20Model%20Context%20Protocol/08%20Accessing%20resources.md)
- [ ] **63** · [Defining prompts](09%20-%20Model%20Context%20Protocol/09%20Defining%20prompts.md)
- [ ] **64** · [Prompts in the client](09%20-%20Model%20Context%20Protocol/10%20Prompts%20in%20the%20client.md)
- [ ] **65** · [MCP review](09%20-%20Model%20Context%20Protocol/11%20MCP%20review.md)
- [ ] **66** · [Quiz on Model Context Protocol](09%20-%20Model%20Context%20Protocol/12%20Quiz%20on%20Model%20Context%20Protocol.md)

### 10. Anthropic Apps: Claude Code & Computer Use
- [ ] **67** · [Anthropic apps](10%20-%20Anthropic%20apps%20-%20Claude%20Code%20and%20computer%20use/01%20Anthropic%20apps.md)
- [ ] **68** · [Claude Code setup](10%20-%20Anthropic%20apps%20-%20Claude%20Code%20and%20computer%20use/02%20Claude%20Code%20setup.md)
- [ ] **69** · [Claude Code in action](10%20-%20Anthropic%20apps%20-%20Claude%20Code%20and%20computer%20use/03%20Claude%20Code%20in%20action.md)
- [ ] **70** · [Enhancements with MCP servers](10%20-%20Anthropic%20apps%20-%20Claude%20Code%20and%20computer%20use/04%20Enhancements%20with%20MCP%20servers.md)

### 11. Agents and Workflows
- [ ] **71** · [Agents and workflows](11%20-%20Agents%20and%20workflows/01%20Agents%20and%20workflows.md)
- [ ] **72** · [Parallelization workflows](11%20-%20Agents%20and%20workflows/02%20Parallelization%20workflows.md)
- [ ] **73** · [Chaining workflows](11%20-%20Agents%20and%20workflows/03%20Chaining%20workflows.md)
- [ ] **74** · [Routing workflows](11%20-%20Agents%20and%20workflows/04%20Routing%20workflows.md)
- [ ] **75** · [Agents and tools](11%20-%20Agents%20and%20workflows/05%20Agents%20and%20tools.md)
- [ ] **76** · [Environment inspection](11%20-%20Agents%20and%20workflows/06%20Environment%20inspection.md)
- [ ] **77** · [Workflows vs agents](11%20-%20Agents%20and%20workflows/07%20Workflows%20vs%20agents.md)
- [ ] **78** · [Quiz on Agents and Workflows](11%20-%20Agents%20and%20workflows/08%20Quiz%20on%20Agents%20and%20Workflows.md)

### 12. Final Assessment
- [ ] **79** · [Final Assessment](12%20-%20Final%20assessment/01%20Final%20Assessment.md)

### 13. Wrapping Up
- [ ] **80** · [Course Wrap Up](13%20-%20Wrapping%20up/01%20Course%20Wrap%20Up.md)
