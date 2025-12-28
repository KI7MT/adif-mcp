import asyncio
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_audit_agent():
    # Define how to start your specific server
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "src/adif_mcp/server.py"],
    )

    print("📡 ADIF Audit Agent: Connecting to Sovereign Node...")

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()

                # List available tools to confirm capabilities
                list_resp = await session.list_tools()
                tools = {t.name for t in list_resp.tools}
                print(f"✅ Connection Established. Capabilities: {', '.join(sorted(tools))}")

                # Helper to execute a tool and display the output
                async def audit_tool(name: str, args: dict):
                    print(f"\n🔍 [Audit] Invoking: {name}")
                    print(f"   Args: {json.dumps(args)}")
                    try:
                        result = await session.call_tool(name, arguments=args)
                        for content in result.content:
                            if content.type == "text":
                                # Parse JSON back if possible for pretty printing,
                                # else print raw
                                try:
                                    data = json.loads(content.text)
                                    print(f"   Result: {json.dumps(data, indent=2)}")
                                except json.JSONDecodeError:
                                    print(f"   Result: {content.text}")
                    except Exception as e:
                        print(f"   ❌ Error: {e}")

                # --- Execute Audit Sequence ---

                # 1. Verify Service Identity
                if "get_service_metadata" in tools:
                    await audit_tool("get_service_metadata", {})

                # 2. Verify Sovereign Data (Country Lookup)
                if "lookup_country" in tools:
                    await audit_tool("lookup_country", {"callsign": "KI7MT"})

                # 3. Verify Analytics (Distance)
                if "calculate_distance" in tools:
                    await audit_tool("calculate_distance", {"start": "FN20", "end": "IO91"})

                # 4. Verify Data Integrity (QSO Validation)
                if "validate_qso" in tools:
                    # Note: Pydantic models in FastMCP tools often require
                    # the argument name 'qso' wrapping the object.
                    qso_payload = {
                        "call": "W1AW",
                        "qso_date": "2025-01-01",
                        "time_on": "14:00:00",
                        "band": "20m",
                        "mode": "cw",
                        "rst_sent": "599",
                    }
                    await audit_tool("validate_qso", {"qso": qso_payload})

                # 5. Verify Integration Stubs (eQSL)
                if "eqsl_query" in tools:
                    await audit_tool("eqsl_query", {"callsign": "KI7MT"})

    except Exception as e:
        print(f"\n❌ Agent Connection Failed: {e}")


if __name__ == "__main__":
    asyncio.run(run_audit_agent())
