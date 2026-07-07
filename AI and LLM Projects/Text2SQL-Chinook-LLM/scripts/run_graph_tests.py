# run_graph_tests.py

import pandas as pd
from datetime import datetime

def run_graph_tests(graph):
    test_questions = [
        "How many customers are there?",
        "How many albums are there?",
        "How many employees are there?",
        "How many tracks are in the database?",
        "What is the total number of invoices?",
    ]

    sample_questions = [
        "How many customers are there?",
        "How many employees are there?",
        "How many albums are there?",
        "How many tracks are in the database?",
        "What is the total number of invoices?",
        "What is the total sales (sum) of all invoices?",
        "What is the total number of genres?",
        "Which country has the most customers?",
        "Which city has the highest total invoice amount?",
        "Who is the best customer (spent the most)?",
        "How many invoices were created in 2009?",
        "How many invoices were created in 2011?",
        "List all employees who are sales agents.",
        "Which artist sold the most tracks?",
        "Which artist earned the most from track sales?",
        "What is the average invoice total?",
        "Which genre is most popular?",
        "How many playlists are there?",
        "Which playlist has the most tracks?",
        "Which media type is used most often?",
        "What is the average length of a track?",
        "List tracks longer than the average track length.",
        "What are the top 5 customers by invoice total?",
        "List invoice count per country.",
        "List customer count per support representative (employee).",
        "What are the albums by artists containing 'black' in their name?",
        "What are the distinct billing countries in invoice table?",
        "Which album has the most tracks?",
        "How many tracks are in each album?",
        "What are the most expensive tracks (by unit price)?",
        "What is the cheapest track?",
        "What is the total number of invoice line items?",
        "What is the total sales grouped by country?",
        "Which sales agent made the most in 2009?",
        "Which sales agent made the most in 2010?",
        "Which sales agent made the most overall?",
        "What are the customers from Brazil?",
        "What are the invoices for customers in Brazil?",
        "What is the most popular genre in each country?",
        "Which customers listened to Rock music?",
        "Which artists wrote Rock music (artist + track count)?",
        "What is the total sales for each artist?",
        "Which artist has the highest number of tracks?",
        "What is the album title with AlbumId 67?",
        "List name and length (in seconds) of tracks between 50 and 70 seconds.",
        "What are the albums by artists whose names have 'the' in them?",
        "Which customers have not made any invoices?",
        "Which tracks are never sold (never appear in invoice_line)?",
        "Which invoices have more than 3 line items?",
        "Which invoice had the highest number of line items?",
        "Which genre has the highest average unit price of tracks?"
    ]
    results = []

    for question in sample_questions:
        output = graph.invoke({"user_question": question})
        results.append({
            "Question": output.get("user_question", ""),
            "Generated SQL": output.get("query", ""),
            "SQL Result": output.get("result", ""),
            "Answer": output.get("answer", ""),
        })

    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = f"test_results_{timestamp}.xlsx"
    df.to_excel(output_file, index=False)
    print(f"✅ Test results saved to: {output_file}")
