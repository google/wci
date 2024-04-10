CREATE TEMP FUNCTION
  get_chat_id(sender STRING,
    receiver STRING)
  RETURNS STRING AS (CONCAT(GREATEST(IFNULL(sender, 'bot'), IFNULL(receiver, 'bot')), '-', LEAST(IFNULL(sender, 'bot'), IFNULL(receiver, 'bot'))));
WITH
  bot AS (
  SELECT
    IFNULL(sender, 'bot') AS number,
    COUNT(*)
  FROM
    `$GOOGLE_CLOUD_PROJECT.wci.chat_leads`
  WHERE
    timestamp BETWEEN TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
    AND TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
  GROUP BY
    1
  ORDER BY
    2 DESC
  LIMIT
    1 ),
  journeys AS (
  SELECT
    get_chat_id(TO_BASE64(SHA256(sender)),
      TO_BASE64(SHA256(receiver))) AS chat_id,
    CONCAT('Using only 2 words in portuguese, what is the customer intent in this chat? ', ARRAY_TO_STRING(ARRAY_AGG(message
        ORDER BY
          TIMESTAMP ASC), '\n')) AS prompt,
    MAX(timestamp) AS last_message_at
  FROM
    `$GOOGLE_CLOUD_PROJECT.wci.chat_leads`
  INNER JOIN
    bot
  ON
    bot.number = IFNULL(receiver, 'bot')
  WHERE
    timestamp BETWEEN TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
    AND TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
  GROUP BY
    1
  ORDER BY
    3 DESC),
  to_predict AS (
  SELECT
    journeys.*
  FROM
    journeys
  LEFT JOIN
    `$GOOGLE_CLOUD_PROJECT.$BQ_DATASET_NAME.topics_clustering` AS storaged
  USING
    (chat_id)
  WHERE
    storaged.chat_id IS NULL )
SELECT
  ml_generate_text_llm_result AS topic,
  CURRENT_TIMESTAMP() AS predicted_at,
  chat_id,
  prompt,
  last_message_at
FROM
  ML.GENERATE_TEXT(MODEL `$GOOGLE_CLOUD_PROJECT.$BQ_DATASET_NAME.gemini-pro`,
    TABLE to_predict,
    STRUCT( 0.1 AS temperature,
      10 AS max_output_tokens,
      0.5 AS top_p,
      20 AS top_k,
      TRUE AS flatten_json_output));