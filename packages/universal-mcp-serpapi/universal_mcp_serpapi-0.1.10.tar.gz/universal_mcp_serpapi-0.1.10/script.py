from universal_mcp.integrations import AgentRIntegration
from universal_mcp.utils.agentr import AgentrClient
from universal_mcp.tools import ToolManager
from universal_mcp_serpapi.app import SerpapiApp
import anyio
from pprint import pprint

integration = AgentRIntegration(name="serpapi", api_key="sk_416e4f88-3beb-4a79-a0ef-fb1d2c095aee", base_url="https://api.agentr.dev")
app_instance = SerpapiApp(integration=integration)
tool_manager = ToolManager()

tool_manager.add_tool(app_instance.google_maps_search)


async def main():
    # Get a specific tool by name
   
    tool=tool_manager.get_tool("google_maps_search")

    if tool:
        pprint(f"Tool Name: {tool.name}")
        pprint(f"Tool Description: {tool.description}")
        pprint(f"Arguments Description: {tool.args_description}")
        pprint(f"Returns Description: {tool.returns_description}")
        pprint(f"Raises Description: {tool.raises_description}")
        pprint(f"Tags: {tool.tags}")
        pprint(f"Parameters Schema: {tool.parameters}")
        
        # You can also get the JSON schema for parameters
    
    # Get all tools
    all_tools = tool_manager.get_tools_by_app()
    print(f"\nTotal tools registered: {len(all_tools)}")
    
    # List tools in different formats
    mcp_tools = tool_manager.list_tools()
    print(f"MCP format tools: {len(mcp_tools)}")
    
    # Execute the tool
    # result = await tool_manager.call_tool(name="list_messages", arguments={"max_results": 2})
    # result = await tool_manager.call_tool(name="get_message", arguments={"message_id": "1985f5a3d2a6c3c8"})
    # result = await tool_manager.call_tool(
    #     name="send_email",
    #     arguments={
    #         "to": "rishabh@agentr.dev",
    #         "subject": " Email",
    #         "body": "<html><body><h1>Hello!</h1><p>This is a <b>test email</b> sent from the script.</p></body></html>",
    #         "body_type": "html"
    #     }
    # )
    # result = await tool_manager.call_tool(name="create_draft", arguments={"to": "rishabh@agentr.dev", "subject": " Draft Email", "body": " test email"})
    # result = await tool_manager.call_tool(name="send_draft", arguments={"draft_id": "r354126479467734631"})
    # result = await tool_manager.call_tool(name="get_draft", arguments={"draft_id": "r5764319286899776116"})
    # result = await tool_manager.call_tool(name="get_profile",arguments={})
    # result = await tool_manager.call_tool(name="list_drafts", arguments={"max_results": 2})
    # result = await tool_manager.call_tool(name="list_labels",arguments={})
    # result = await tool_manager.call_tool(name="create_label",arguments={"name": "test_label"})
    # Example: Send new email
    # result = await tool_manager.call_tool(name="send_email", arguments={"to": "rishabh@agentr.dev", "subject": "Meeting Tomorrow", "body": "Let's meet at 2pm"})
    
    # Example: Reply to thread (using thread_id)
    result = await tool_manager.call_tool(name="google_maps_search", arguments={"q": " 2 cafe in hsr layout"})
    # import json
    # with open("result.json", "w", encoding="utf-8") as f:
    #     json.dump(result, f, ensure_ascii=False, indent=2)
    print(result)
    print(type(result))

if __name__ == "__main__":
    anyio.run(main)