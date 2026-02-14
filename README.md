# football-dialogue-agent
LLM-powered football assistant that performs structured information extraction and real-time API integration for domain-specific question answering.
## Architecture

User Input  
→ LLM (Intent + Slot Extraction)  
→ Slot-Based Routing  
→ Football-Data API  
→ Generated Response  

## Supported Slots

- lastOpponent  
- lastScore  
- leaguePosition  
- manager  
- nextGameDate  
- nextOpponent  
- numGamesPlayed  
- playingNow  
- winLossRecord  
