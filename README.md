# adif-mcp
📡 Universal ADIF schema + MCP tools for amateur radio logging.

This project implements the [ADIF 3.1.5 specification](https://adif.org.uk/315/ADIF_315.htm) as a **core library** for amateur radio logging systems.  
It provides:

- ✅ Validation & normalization of ADIF records  
- 📂 Unified schema for consistent QSO storage and exchange  
- 🤖 MCP-ready tools for safe AI-agent access  
- 🔌 Foundation for service adapters (e.g., LoTW, eQSL)  

## Why?
Every amateur radio logger supports ADIF, but implementations are fragmented.  
`adif-mcp` offers a **single, standards-based interface** to make QSO data portable, auditable, and agent-friendly.  

## Next Steps
- Build `adif-mcp-lotw` and `adif-mcp-eqsl` adapters  
- Expose MCP tools for validation, award tracking, and service sync  
- Support cross-logger interoperability with AI-driven agents  

## License
MIT — open and free for amateur radio use.
