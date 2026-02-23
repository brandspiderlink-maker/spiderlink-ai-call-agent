from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import os
from openai import OpenAI

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a polite and helpful Spiderlink Broadband sales and support executive.
Reply in simple Hindi like a real human.
Keep replies short (max 2 sentences).
"""

@app.post("/voice")
async def voice(request: Request):
    form = await request.form()
    user_input = form.get("SpeechResult")

    response = VoiceResponse()

    if not user_input:
        gather = Gather(
            input="speech",
            action="/voice",
            method="POST",
            language="hi-IN"
        )
        gather.say(
            "Namaste. Aapka  Spiderlink Broadband main suaagat h . Main aapki kaise madad kar sakta hoon?",
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
        ]
    )

    reply = ai_response.choices[0].message.content.strip()

    gather = Gather(
        input="speech",
        action="/voice",
        method="POST",
        language="hi-IN"
    )

    gather.say(reply, voice="Polly.Aditi", language="hi-IN")
    gather.say("Kya aap aur kuch jaankari dena chahenge?", voice="Polly.Aditi", language="hi-IN")

    response.append(gather)

    return Response(content=str(response), media_type="application/xml")
