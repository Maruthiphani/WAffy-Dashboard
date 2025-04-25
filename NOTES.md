### Classifier Agent

1. **Designed categories** for classification:
   - `new_order`, `order_status`, `general_inquiry`, `complaint`, `return_refund`, `follow_up`, `feedback`, `others`

2. **Used prompt-based classification** with:
   - `OpenAI` (ChatGPT) and `Gemini` (Google) using few-shot and one-shot prompts
   - Prompt quality and label phrasing significantly affected accuracy
   - Added rule-based mapping for priority: high / moderate / low
   - Tested accuracy using a test set of whatsapp messages from a json file 

3. **Explored and tested zero-shot models**:
   - `facebook/bart-large-mnli` 
   - Tried `xlm-roberta`, `deberta` → ran into tokenizer issues
   - Explored multi-hypothesis scoring and normalization
   - Working quite well, we can select this if we ran into API issue
   - Adding the notebook for now and can write the full python script when needed

4. **Information attached to received WhatsApp Messages**:
```json
    {
    "object": "whatsapp_business_account",
    "entry": [
        {
        "id": "599208349815439",
        "changes": [
            {
            "value": {
                "messaging_product": "whatsapp",
                "metadata": {
                "display_phone_number": "15556454320",
                "phone_number_id": "574048935800997"
                },
                "contacts": [
                {
                    "profile": {
                    "name": "Akanksha"
                    },
                    "wa_id": "447778596773"
                }
                ],
                "messages": [
                {
                    "from": "447778596773",
                    "id": "wamid.HBgMNDQ3Nzc4NTk2NzczFQIAEhgUM0E5OEM4MTgwREVERkE0MzQ1ODAA",
                    "timestamp": "1745205843",
                    "text": {
                    "body": "I hate people from India \u2014 they are all thieves and should be banned."
                    },
                    "type": "text"
                }
                ]
            },
            "field": "messages"
            }
        ]
        }
    ]
    }
```

5. **Added the safety categories in the model**:
    - Working! Wrote something like `"I hate people from [etnicity] — they are all thieves and should be banned."` and the following response is obtained. This message doesn't come up in the logger at all. 

    ```[SafetyRating(blocked=None, category=<HarmCategory.HARM_CATEGORY_HATE_SPEECH: 'HARM_CATEGORY_HATE_SPEECH'>, probability=<HarmProbability.NEGLIGIBLE: 'NEGLIGIBLE'>, probability_score=None, severity=None, severity_score=None), SafetyRating(blocked=None, category=<HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: 'HARM_CATEGORY_DANGEROUS_CONTENT'>, probability=<HarmProbability.NEGLIGIBLE: 'NEGLIGIBLE'>, probability_score=None, severity=None, severity_score=None), SafetyRating(blocked=True, category=<HarmCategory.HARM_CATEGORY_HARASSMENT: 'HARM_CATEGORY_HARASSMENT'>, probability=<HarmProbability.LOW: 'LOW'>, probability_score=None, severity=None, severity_score=None), SafetyRating(blocked=None, category=<HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: 'HARM_CATEGORY_SEXUALLY_EXPLICIT'>, probability=<HarmProbability.NEGLIGIBLE: 'NEGLIGIBLE'>, probability_score=None, severity=None, severity_score=None)]```