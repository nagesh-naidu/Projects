# agent_test_runner.py

import pandas as pd

def test_agent(agent_executor, questions, output_excel_path="agent_test_results.xlsx"):
    """
    Runs a set of natural language questions through the agent and saves the final answers to Excel.
    
    Parameters:
        agent_executor: The initialized agent (e.g. from create_react_agent).
        questions (list): List of natural language questions.
        output_excel_path (str): File path to save the Excel results.
    
    Returns:
        pandas.DataFrame: The test results as a DataFrame.
    """
    results = []

    for question in questions:
        print(f"Testing: {question}")
        try:
            response = agent_executor.invoke({
                "messages": [{"role": "user", "content": question}]
            })
            final_answer = response["messages"][-1].content.strip()
            results.append({
                "Question": question,
                "Final Answer": final_answer
            })
        except Exception as e:
            results.append({
                "Question": question,
                "Final Answer": f"Error: {str(e)}"
            })

    df = pd.DataFrame(results)
    df.to_excel(output_excel_path, index=False)
    print(f"\n✅ Results saved to: {output_excel_path}")
    return df
