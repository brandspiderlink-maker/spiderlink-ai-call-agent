from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import os
from openai import OpenAI

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a polite and helpful Spiderlink Broadband sales and support executive.

Understand the customer's intent from what they say:
1. New Connection
2. Plan Inquiry
3. Complaint
4. Billing Issue

Reply like a real human in simple Hindi (Hinglish allowed).
Keep replies short (max 2 sentences).
Ask follow-up questions where needed.

If it's a complaint, say:
"Main aapki complaint technical team ko transfer kar raha hoon."

Never guess or invent pricing.
Sound friendly and professional.
"""

@app.post("/voice")
async def voice(request: Request):
    form = await request.form()
    user_input = form.get("SpeechResult")

    response = VoiceResponse()

    if not user_input:
        gather = Gather(input="speech", action="/voice", method="POST")
        gather.say(
            "Namaste. Aap Spiderlink Broadband se jude hain. Main aapki kaise madad kar sakta hoon?",
            voice="Polly.Aditi",
            language="hi-IN"
        )
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")

    ai_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        temperature=0.4
    )

    reply = ai_response.choices[0].message.content.strip()

    response.say(
        reply,
        voice="Polly.Aditi",
        language="hi-IN"
    )

    gather = Gather(input="speech", action="/voice", method="POST")
    gather.say(
        "Kya aap aur kuch jaankari dena chahenge?",
        voice="Polly.Aditi",
        language="hi-IN"
    )
    response.append(gather)

    return Response(content=str(response), media_type="application/xml")

import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
