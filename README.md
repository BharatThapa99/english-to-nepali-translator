# english-to-nepali-translator
Uses unofficial google translator endpoint to translate entire file from English to Nepali.
The endpoint `https://translate.google.com/m?hl=en&sl=en&tl=ne&ie=UTF-8&prev=_m&q=text+to+translate`
where, 
- **sl** is source language
- **tl** is target language 
- **q** is a text to translate.
Sends a get request to above endpoint and extracts the translated part from the json output.
The code is written for test purpose for a specific dataset that has multiple json objects as Context and Response.
When a fullstop or question mark is found in the q parameter the endpoint sense another json object so a loop has to be used to extract the translated sentence.

## Findings
- on first run, request time out occured after 300 requests
- on second run, request time out occured after 1000 requests
