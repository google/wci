
curl -X POST "http://127.0.0.1:${PORT}/webhook-wci" \
-H "Content-Type: application/json" \
-d '{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "1234",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "+1 234-5678",
              "phone_number_id": "12345678"
            },
            "contacts": [
              {
                "profile": {
                  "name": "Test, Test"
                },
                "wa_id": "123"
              }
            ],
            "messages": [
              {
                "from": "12345678",
                "id": "test_1",
                "timestamp": "1723232055",
                "text": {
                  "body": "This is a local test"
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
}'