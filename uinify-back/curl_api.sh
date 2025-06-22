#!/bin/bash

curl \
    -X POST 'http://localhost:5000/user' \
    -H 'Content-Type: application/json' \
    -d '{"username": "eduardo", "password": "123456"}'

curl \
    -X GET 'http://localhost:5000/users' \
    -H 'Content-Type: application/json' \

curl \
    -X POST 'http://localhost:5000/user' \
    -H 'Content-Type: application/json' \
    -d '{"username": "murilo", "password": "123456"}'

curl \
    -X GET 'http://localhost:5000/users' \
    -H 'Content-Type: application/json' \

curl \
    -X DELETE 'http://localhost:5000/user/1' \
    -H 'Content-Type: application/json' \

curl \
    -X GET 'http://localhost:5000/users' \
    -H 'Content-Type: application/json' \

curl \
    -X POST 'http://localhost:5000/component' \
    -H 'Content-Type: application/json' \
    -d '{
            "user_id": 2,
            "title": "Simple Card",
            "description": "A responsive card with Tailwind CSS.",
            "framework": "HTML/CSS/JS",
            "category": "Cards",
            "tags": ["card", "tailwind", "responsive"],
            "inputType": "HTML",
            "includeTailwind": true,
            "code": "<div class=\"p-4 bg-white rounded shadow\">Hello!</div>"
         }'

curl \
    -X GET 'http://localhost:5000/components' \
    -H 'Content-Type: application/json' \

sleep 2

curl \
    -X PUT 'http://localhost:5000/component/1' \
    -H 'Content-Type: application/json' \
    -d '{
            "user_id": 2,
            "title": "Complex Card",
            "description": "A responsive card with Tailwind CSS.",
            "framework": "HTML/CSS/JS",
            "category": "Cards",
            "tags": ["card", "tailwind", "responsive"],
            "inputType": "HTML",
            "includeTailwind": true,
            "code": "<div class=\"p-4 bg-white rounded shadow\">Hello!</div>"
         }'

curl \
    -X GET 'http://localhost:5000/components' \
    -H 'Content-Type: application/json' \

curl \
    -X DELETE 'http://localhost:5000/component/1' \
    -H 'Content-Type: application/json' \

curl \
    -X GET 'http://localhost:5000/components' \
    -H 'Content-Type: application/json' \

curl \
    -X POST 'http://localhost:5000/component' \
    -H 'Content-Type: application/json' \
    -d '{
            "user_id": 2,
            "title": "Simple Card",
            "description": "A responsive card with Tailwind CSS.",
            "framework": "HTML/CSS/JS",
            "category": "Cards",
            "tags": ["card", "tailwind", "responsive"],
            "inputType": "HTML",
            "includeTailwind": true,
            "code": "<div class=\"p-4 bg-white rounded shadow\">Hello!</div>"
         }'

curl \
    -X GET 'http://localhost:5000/components' \
    -H 'Content-Type: application/json' \

curl \
    -X POST 'http://localhost:5000/component' \
    -H 'Content-Type: application/json' \
    -d '{
            "user_id": 2,
            "title": "Simple Card",
            "description": "A responsive card with Tailwind CSS.",
            "framework": "HTML/CSS/JS",
            "category": "Cards",
            "tags": ["card", "tailwind", "responsive"],
            "inputType": "HTML",
            "includeTailwind": true,
            "code": "<div class=\"p-4 bg-white rounded shadow\">Hello!</div>"
         }'

curl \
    -X GET 'http://localhost:5000/components' \
    -H 'Content-Type: application/json' \

curl \
    -X DELETE 'http://localhost:5000/user/2' \
    -H 'Content-Type: application/json'

curl \
    -X GET 'http://localhost:5000/components' \
    -H 'Content-Type: application/json' \
