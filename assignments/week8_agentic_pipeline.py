"""
Week 8 - Build an Agentic AI Pipeline
A basic single-agent pipeline with tools, conditional routing, retry logic,
error handling, and trajectory tracking.
"""

import json
import time
import random


# ---- TOOLS (with JSON schema) ----

TOOLS = {
    "calculator": {
        "name": "calculator",
        "description": "Performs basic math operations",
        "input_schema": {"expression": "string"},
        "output_schema": {"result": "number"}
    },
    "keyword_extractor": {
        "name": "keyword_extractor",
        "description": "Extracts keywords from text",
        "input_schema": {"text": "string"},
        "output_schema": {"keywords": "list"}
    },
    "general_responder": {
        "name": "general_responder",
        "description": "Handles general queries",
        "input_schema": {"query": "string"},
        "output_schema": {"response": "string"}
    }
}


def calculator_tool(expression):
    """Tool: evaluate a math expression."""
    try:
        result = eval(expression)
        return {"result": result, "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}


def keyword_extractor_tool(text):
    """Tool: extract keywords from text."""
    stop_words = {"the", "is", "a", "an", "in", "of", "and", "to", "for", "it", "on", "that", "this", "with"}
    words = text.lower().split()
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return {"keywords": list(set(keywords)), "status": "success"}


def general_responder_tool(query):
    """Tool: give a general response."""
    return {"response": f"I received your query: '{query}'. This is a general response.", "status": "success"}


# ---- CONDITIONAL ROUTING ----

def route_query(query):
    """Route query to the right tool based on keywords."""
    query_lower = query.lower()
    if any(word in query_lower for word in ["calculate", "math", "add", "subtract", "multiply", "+", "-", "*", "/"]):
        return "calculator"
    elif any(word in query_lower for word in ["keyword", "extract", "words", "find words"]):
        return "keyword_extractor"
    else:
        return "general_responder"


# ---- ERROR HANDLING WITH RETRY ----

def execute_with_retry(tool_func, tool_input, max_retries=3):
    """Execute a tool with retry logic."""
    for attempt in range(1, max_retries + 1):
        try:
            # Simulate random failure (20% chance)
            if random.random() < 0.2:
                raise ConnectionError("Simulated network error")
            result = tool_func(tool_input)
            return result, attempt
        except Exception as e:
            print(f"    [Retry {attempt}/{max_retries}] Error: {e}")
            if attempt == max_retries:
                return {"error": str(e), "status": "failed"}, attempt
            time.sleep(0.5)


# ---- STATEFUL GRAPH / PIPELINE ----

class AgentPipeline:
    """A simple stateful agent pipeline with nodes, edges, routing, and tracking."""

    def __init__(self):
        self.state = {}
        self.trajectory = []
        self.metrics = {"total_tasks": 0, "completed": 0, "failed": 0, "total_retries": 0, "total_time": 0}

    def run(self, query):
        """Run the full pipeline for a query."""
        start_time = time.time()
        self.metrics["total_tasks"] += 1
        print(f"\n{'='*60}")
        print(f"  Query: {query}")
        print(f"{'='*60}")

        # Node 1: Analyze query
        step1 = {"node": "QueryAnalyzer", "input": query}
        self.state["query"] = query
        print(f"  [Node 1] QueryAnalyzer -> Analyzing query...")
        self.trajectory.append(step1)

        # Node 2: Route to tool
        tool_name = route_query(query)
        step2 = {"node": "Router", "routed_to": tool_name}
        self.state["tool"] = tool_name
        print(f"  [Node 2] Router -> Routed to: {tool_name}")
        self.trajectory.append(step2)

        # Node 3: Execute tool with retry
        tool_map = {
            "calculator": calculator_tool,
            "keyword_extractor": keyword_extractor_tool,
            "general_responder": general_responder_tool
        }

        # Prepare input based on tool
        if tool_name == "calculator":
            # Extract math expression from query
            expression = query.lower().replace("calculate", "").replace("math", "").strip()
            tool_input = expression
        elif tool_name == "keyword_extractor":
            tool_input = query
        else:
            tool_input = query

        print(f"  [Node 3] ToolExecutor -> Running {tool_name}...")
        result, attempts = execute_with_retry(tool_map[tool_name], tool_input)
        self.metrics["total_retries"] += (attempts - 1)

        step3 = {"node": "ToolExecutor", "tool": tool_name, "result": result, "attempts": attempts}
        self.trajectory.append(step3)
        self.state["result"] = result

        # Node 4: Generate response
        if result.get("status") == "success":
            self.metrics["completed"] += 1
            print(f"  [Node 4] ResponseGenerator -> Success!")
        else:
            self.metrics["failed"] += 1
            print(f"  [Node 4] ResponseGenerator -> Failed after {attempts} attempts")

        elapsed = time.time() - start_time
        self.metrics["total_time"] += elapsed

        step4 = {"node": "ResponseGenerator", "output": result, "time": round(elapsed, 3)}
        self.trajectory.append(step4)

        print(f"\n  Result: {json.dumps(result, indent=4)}")
        print(f"  Time: {elapsed:.3f}s | Attempts: {attempts}")
        return result

    def show_trajectory(self):
        """Show the full trajectory of all steps."""
        print(f"\n{'='*60}")
        print("  TRAJECTORY EVALUATION")
        print(f"{'='*60}")
        for i, step in enumerate(self.trajectory):
            print(f"  Step {i+1}: {json.dumps(step)}")

    def show_metrics(self):
        """Show task completion rate and cost metrics."""
        print(f"\n{'='*60}")
        print("  METRICS DASHBOARD")
        print(f"{'='*60}")
        total = self.metrics["total_tasks"]
        completed = self.metrics["completed"]
        rate = (completed / total * 100) if total > 0 else 0
        print(f"  Total Tasks:       {total}")
        print(f"  Completed:         {completed}")
        print(f"  Failed:            {self.metrics['failed']}")
        print(f"  Completion Rate:   {rate:.1f}%")
        print(f"  Total Retries:     {self.metrics['total_retries']}")
        print(f"  Total Time:        {self.metrics['total_time']:.3f}s")
        print(f"  Avg Time/Task:     {self.metrics['total_time']/total:.3f}s" if total > 0 else "")


# ---- MAIN ----

if __name__ == "__main__":
    agent = AgentPipeline()

    # Demo queries
    queries = [
        "calculate 25 + 17 * 3",
        "extract keywords from: The agent pipeline uses nodes and edges for routing",
        "What is the weather today?",
        "math 100 / 4 + 50",
        "find words in: Python is a great programming language for AI",
    ]

    print("\n" + "=" * 60)
    print("   AGENTIC AI PIPELINE - DEMO")
    print("=" * 60)

    for q in queries:
        agent.run(q)

    # Show trajectory and metrics
    agent.show_trajectory()
    agent.show_metrics()
