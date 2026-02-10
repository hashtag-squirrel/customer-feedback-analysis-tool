# Customer Feedback Analysis Tool

This project is created as a code challenge.

The underlying objective is to build a tool that processes written customer feedback and automatically:

1. Classifies the sentiment
2. Identifies the topics to route the feedback to the appropriate team
3. Stores the feedback for later analysis
4. Alerts a team when an immediate response is required

## Design Rationale

### Clarifying questions

Clarifying questions I would ask about this project would be the following:

1. The assignment specifies that the team should be alerted when immediate action is needed. Is there a specific system/tool through which the team should be alerted?
2. The requirements specify that the API responds within 500ms. What does the API response time refer to: a response to customer upon sending of the feedback, the response from the AI with the classification and identification of the topics or the response towards the team?
3. Should the customer receive a personalized response when sending the feedback, depending on the feedback's sentiment, or should they receive a generic response thanking them for the feedback?

### Approaches considered

I approached the assignment as a two-part problem, building the backend to handle the requests and the AI integration.

#### The backend

1. Django (full-stack framework)

    Since I have a lot of experience with Django, this was the first approach I considered. Django would offer a versatile framework that let's me build a front- and backend with integrated database in a short amound of time.
    It provides a mature ORM, migrations, and many built-in features that reduce boilerplate. However, for this challenge, Django felt heavier than necessary. The task focuses on API design, background processing, and AI integration rather than server-side rendering or a rich admin interface. Using Django would introduce additional complexity and opinionated structure that does not directly contribute to solving the core problem.

2. Building a backend/API from scratch

    Building a backend from scratch without a major framework was also considered. While this would give maximum control over architecture and dependencies, it would require reimplementing common concerns such as request handling, validation, error management, and testing infrastructure. Given the time constraints and the availability of well-supported frameworks, this approach would provide low value relative to the effort required and increase the risk of bugs in non-core areas.

3. Building just a backend using FastAPI with PostgreSQL tables

    FastAPI was chosen as a middle ground between flexibility and productivity. It is well-suited for API-first systems, has excellent documentation, and provides strong support for asynchronous code, which is useful for handling background processing and external AI calls. FastAPI’s request validation and type hints help make API contracts explicit and testable, while keeping the overall system lightweight. Combined with a small number of PostgreSQL tables, this approach allows focusing on the core challenges of the task: reliability, latency, AI integration, and failure handling, without unnecessary framework overhead.

#### The AI integration

For the AI integration, I considered both Google’s Gemini API and OpenAI’s API. Both are capable of handling sentiment analysis and topic classification at the required scale. I chose OpenAI primarily due to prior familiarity and ease of access through its own [Python module](https://github.com/openai/openai-python), which should reduce integration time and allow me to focus on system design, failure handling, and validation rather than provider-specific setup.

Further down the line, the AI integration can of course be adapted to any other AI provider or even a self-hosted model.

### Why am I using this approach over alternatives

As pointed out above, I chose to use FastAPI with a PostgreSQL database due to its relative simplicity. Since the assignment merely asks for a backend for this problem, Django is unneccessarily overpowered for this and building from scratch was rejected due to time concerns.

As for the AI integration, OpenAI's API was chosen since this seemed like the more familiar option to me.

### What I am intentionally not building

1. Frontend or user-facing UI

    The scope of this task is explicitly focused on backend design, API behavior, and AI integration. As a result, no frontend application or user interface is implemented. All functionality is exposed via APIs and can be exercised through automated tests or simple HTTP requests. A frontend could be added later without impacting the core system design.

2. Dedicated message queue or event streaming system

    The system does not use a dedicated queuing solution such as SQS, RabbitMQ, or Kafka. Instead, the database is used as a simple, reliable queue by marking feedback items as pending and processing them asynchronously. This approach reduces operational complexity and is sufficient for the expected load in this exercise. In a production environment or at higher scale, this component could be replaced with a proper message queue to improve throughput, parallelism, and failure isolation without changing the API or business logic.
