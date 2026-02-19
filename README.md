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

3. Building just a backend using FastAPI with SQLite tables

    FastAPI was chosen as a middle ground between flexibility and productivity. It is well-suited for API-first systems, has excellent documentation, and provides strong support for asynchronous code, which is useful for handling background processing and external AI calls. FastAPI’s request validation and type hints help make API contracts explicit and testable, while keeping the overall system lightweight. Combined with a small number of SQLite tables, this approach allows focusing on the core challenges of the task: reliability, latency, AI integration, and failure handling, without unnecessary framework overhead.

#### The AI integration

For the AI integration, I considered both Google’s Gemini API and OpenAI’s API. Both are capable of handling sentiment analysis and topic classification at the required scale. I chose OpenAI primarily due to prior familiarity and ease of access through its own [Python module](https://github.com/openai/openai-python), which should reduce integration time and allow me to focus on system design, failure handling, and validation rather than provider-specific setup.

Further down the line, the AI integration can of course be adapted to any other AI provider or even a self-hosted model.

### Why am I using this approach over alternatives

As pointed out above, I chose to use FastAPI with a SQLite database due to its relative simplicity. Since the assignment merely asks for a backend for this problem, Django is unneccessarily overpowered for this and building from scratch was rejected due to time concerns.

As for the AI integration, OpenAI's API was chosen since this seemed like the more familiar option to me.

### What I am intentionally not building

1. Frontend or user-facing UI

    The scope of this task is explicitly focused on backend design, API behavior, and AI integration. As a result, no frontend application or user interface is implemented. All functionality is exposed via APIs and can be exercised through automated tests or simple HTTP requests. A frontend could be added later without impacting the core system design.

2. Dedicated message queue or event streaming system

    The system does not use a dedicated queuing solution such as SQS, RabbitMQ, or Kafka. Instead, the database is used as a simple, reliable queue by marking feedback items as pending and processing them asynchronously. This approach reduces operational complexity and is sufficient for the expected load in this exercise. In a production environment or at higher scale, this component could be replaced with a proper message queue to improve throughput, parallelism, and failure isolation without changing the API or business logic.

## Setup & Usage

### Running the app

To run the app, you need to have Docker. Then, in a console in the root directory you can use `docker compose up` to build and run the app.

### Environment Setup

In order for the app to run correctly, you need to configure the `.env` file in the root directory. There is a file called `.env.example` that can be used as a blueprint. You only need to add your own OpenAI API key to run the app.

## Assumptions

Several assumptions were made in the beginning based on the open-ended requirements for the project.

1. How/where should the team be alerted in situations requiring immediate action?
    I decided to use [ntfy](https://ntfy.sh/) for my solution, but it can of course be adjusted to any other application like Teams, Slack or whichever system is used by simply expanding or replacing with another service.

2. The API should respond within 500ms, but it is not specified which response is meant.
    My assumption is that this is the initial API that receives the POST request including the feedback. I designed the app in a way that the call to OpenAI to process sentiment and topics is a background task and doesn't block the POST API. Therefore, it should easily handle to send its response within 500ms and the frontend can then display a message to the customer acccordingly.

3. Should the customer receive a personalized response when sending the feedback?
    My assumption here was that if I waited for an AI generated response to the customer, I couldn't maintain the time limit of 500ms in every case, since there would be a dependency on the AI integration, which could either be slow or even down. Therefore, I opted to just send 200 OK.

## Technical Decisions

- Abstract Base Classes for clients
    I built both the AI client and the notification client with an abstract base class so they can be expanded with different concrete clients down the road depending on need.

- Database design and background task
    I initially considered having two different tables, one for the feedback itself and one functioning as a "queue", but instead I added a flag for processed into the original table.
    I do have a separate table for the feedback received, which doesn't include the AI response's content and the processed flag, so I can omit the check that these values should not be set on the POST call.
    When the POST call is made, a background task asynchronously processes the feedback through the OpenAI API and saves the response in the original table feedback table.
    As mentioned above, this is not a scalable solution, but it can be adapted by adding a proper queuing mechanism instead of using the table to keep track of the status of the feedback.

- API currently built without security mechanisms
    Currently, the feedback API is unguarded. In order to deploy it publicly, it would need to be secured properly with an authentication solution so that not anyone can send get requests to our feedback.

- Using SQLAlchemy
    FastAPI comes with SQLAlchemy. Currently, I am using SQLite, but it is easy to switch to any other more scalable database thanks to this.

- Docker startup
    I made a docker compose file so that the application can be run with a single command. Once it runs, one can sent post requests to the endpoint on localhost, as well as observe the health check being performed periodically.

- ntfy as notification service
    I chose ntfy as a simple notification service, but this can be replaced with Teams or Slack or other services.

- Generally, I was trying to use modern Python with type hints, in order to make my code more robust against mistakes.

## AI Integration

For the AI integration, I created an abstract base class `AiClient` and a concrete class for the OpenAI API. The sentiments, topics, response schema and prompt are properties of the base class, but can be overwritten in another concrete implementation if A/B testing is needed.

### Prompt design

#### Sentiment

My initial design includes a simple division of three sentiments, positive, neutral and negative. In a more advanced version of the tool, this could be extended with e.g. more sentiments like "excellent" and "critical" or instead replaced or complemented by a scale of sentiments from 1-10.

#### Topics

The current list of topics includes 'login', 'performance', 'billing', 'ux', 'responses', 'customer service', and 'other'. Since it is designed as a simple list that is passed into the prompt, it can easily be adjusted to include more or less topics.

#### Schema

The prompt specifies the response schema as a dict including sentiment and topics, so the response can be parsed and saved in the database.

#### Prompt

The prompt itself is kept simple. Since the response does not reach the customer but only internal teams, and the response consists merely of the sentiment and topics, it specifies the type of message received and the return format.

#### Other considerations

Since sentiment and topics are simple lists, these could also be parsed from a configuration file to make it configurable for other departments.

### Handling non-deterministic outputs

To avoid too much variation in outputs, the prompt clearly specifies the output format and schema, as well as the parameters for the two desired keys sentiment and topics. This reduces the chance for random responses.
Currently, there are no metrics to observe the responses, but it could be adjusted to send alerts if there are numerous non-fitting responses.

### Edge cases

The current prompt is not fitted to handle sarcastic tone. Since sarcasm is notoriously hard to understand especially in written context without tone and facial expression, even for humans, I assume it might be even harder for the AI to distinguish it. One could try to adjust the prompt to tell the AI to look out for sarcasm, as well as gibberish.

### Error handling and caching strategies

The AI integration is using several checks to verify the response is correct JSON and the parsed response contains the desired keys.

In case the AI takes a long time to respond or is not available, the feedback object stays in the database with a flag 'processed=False' and will be processed on next start of the app. The processing of unprocessed feedback could be adjusted to be a recurring action instead of just on start-up.

## Failure Modes

1. The application may fail already on startup if the .env file is not present or correctly setup or if the file paths are in some way incorrect. It would be noticeable by `docker compose up` failing and would mean the whole application doesn't work and can't receive feedback. This could be handled by adding safety checks for the existence of the .env file as well as file paths.

2. Another fail scenario could be that the OpenAI (or other AI API) limit might be reached. The application would then receive the correct feedback, but calling the AI would fail. This would need to be monitored via their dashboard, however, I have added a try/except statement to catch these errors. Ideally, this could be expanded to have an automatic retry functionality or send a notification to the responsible team for billing.

3. The third way the application may fail is if a user inputs feedback including prompt injection. The prompt is not safeguarding against that in any way, so a user could well give contradicting instructions to the AI to skew the response. In that case, the application would recognize that the response does not match the required JSON format and give an error.

## Production Considerations

- AI monitoring (accuracy, latency, cost)
    In the case of OpenAi, cost monitoring can be done through their dashboard. Cost depends on the number of tokens used, which in turn depend on the length of the input and the length of the generated response. Using a relative short format JSON response is quite economical. Cost can become bigger with longer feedback messages though.
    As for the accuracy of the model, this could be checked by sending a bulk of feedback messages with different contents and then analyzing them for the sentiment and topics using e.g. pandas.

- Observability for debugging
    The application would benefit from a proper logging system. Due to time constraints this was left out and there are merely a few print statements and errors raised.

- Prompt versioning / A/B testing
    There currently is only one prompt in the base class, however, it would be possible to have a random choice of prompts either in the base class or per concrete class to do A/B testing. Furthermore, it is possible to adjust the lists of sentiments and topics to see how much the results differ.

- Scaling to 10x
    At its current state, the feedback API itself can handle a higher volume. However, if one wanted to make sure that it is performing at peak, one could add a load balancer to handle incoming traffic more efficiently.
