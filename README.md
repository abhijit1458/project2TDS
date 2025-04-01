# Project - TDS Solver

## Background

You are a clever student who has joined [IIT Madras’ Online Degree in Data Science](https://study.iitm.ac.in/ds/). You have just enrolled in the [Tools in Data Science](https://tds.s-anand.net/#/) course. <br>

To make your life easier, It is an LLM-based application that can automatically answer any of the graded assignment questions. <br>

Specifically, It consists of building and deployment of an API that accepts any question from one of these 5 graded assignments: <br>

*   [Graded Assignment 1](https://exam.sanand.workers.dev/tds-2025-01-ga1)
*   [Graded Assignment 2](https://exam.sanand.workers.dev/tds-2025-01-ga2)
*   [Graded Assignment 3](https://exam.sanand.workers.dev/tds-2025-01-ga3)
*   [Graded Assignment 4](https://exam.sanand.workers.dev/tds-2025-01-ga4)
*   [Graded Assignment 5](https://exam.sanand.workers.dev/tds-2025-01-ga5)

… and responds with the answer to enter in the assignment. <br>

## About the API

This application exposes an API endpoint at [http://13.48.149.133/api](http://13.48.149.133/api). <br>

The endpoint accepts a POST request, e.g. POST http://13.48.149.133/api with the question as well as optional file attachments as multipart/form-data. <br>

For example, here’s how anyone can make a request:

```
curl -X POST "http://13.48.149.133/api" \
  -H "Content-Type: multipart/form-data" \
  -F "question=Download and unzip file abcd.zip which has a single extract.csv file inside. What is the value in the "answer" column of the CSV file?" \
  -F "file=@abcd.zip"
```
The response must be a JSON object with a single text (string) field: answer that can be directly entered in the assignment. For example:
```
{
  "answer": "1234567890"
}
```

