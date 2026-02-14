# football-dialogue-agent

LLM-powered football assistant that performs structured information extraction and real-time API integration for domain-specific question answering.

## Architecture

User Input  
→ LLM (Structured Intent & Slot Extraction in JSON)
→ Slot-Based Routing  
→ Football-Data API  
→ Generated Response  

## Domain Schema

Intent: `GetInfo`  
Required slot: `team`  
Optional slot list: one or more of the following:

- lastOpponent  
- lastScore  
- leaguePosition  
- manager  
- nextGameDate  
- nextOpponent  
- numGamesPlayed  
- playingNow  
- winLossRecord

## Tech Stack

- Python
- Ollama (local LLM inference)
- Football-Data REST API
- Requests library

