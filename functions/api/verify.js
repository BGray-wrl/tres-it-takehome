const OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions";
const MODEL = "google/gemini-3-flash-preview";

const PROMPT_TEMPLATE = (brand, abv) => `You are verifying an alcohol bottle label for TTB (Alcohol and Tobacco Tax and Trade Bureau) compliance.

Examine this label image and verify three things:

1. BRAND NAME: Does the label show the brand "${brand}"?
   - PASS only if the brand name on the label is the same brand, allowing only for
     capitalization differences. Example: "Stone's Throw" matches "STONE'S THROW".
   - FAIL if the label shows a different brand name — different words mean a definite fail.
     Example: "MOUNTAIN RIDGE SPIRITS" does NOT match "OLD TOM DISTILLERY".
   Set "found" to the exact brand text visible on the label, or null if none.

2. ABV: Does the label show "${abv}%" alcohol by volume?
   - PASS if the numeric value matches (e.g. label shows "45%" or "45% Alc./Vol." and expected is "45").
   - FAIL if the numeric value differs.
   Set "found" to the exact ABV text visible on the label, or null if none.

3. GOVERNMENT WARNING: Is the following EXACT text present?
   Requirements (ALL must be met):
   a) The prefix "GOVERNMENT WARNING:" must be in ALL CAPS. Title case ("Government Warning:")
      or any other casing is a FAIL.
   b) The full statement must match word-for-word (both clauses required):
      "GOVERNMENT WARNING: (1) ACCORDING TO THE SURGEON GENERAL, WOMEN SHOULD NOT DRINK ALCOHOLIC BEVERAGES DURING PREGNANCY BECAUSE OF THE RISK OF BIRTH DEFECTS. (2) CONSUMPTION OF ALCOHOLIC BEVERAGES IMPAIRS YOUR ABILITY TO DRIVE A CAR OR OPERATE MACHINERY, AND MAY CAUSE HEALTH PROBLEMS."
   c) The warning must be legible — not printed in illegibly tiny text.
   PASS if all three are met. FAIL if the text is absent, uses wrong casing, has missing or
   altered words, is missing either clause, or is unreadably small.

Respond ONLY with valid JSON — no markdown, no explanation, just the JSON object:
{
  "brand": { "pass": true, "found": "exact text on label or null", "notes": "" },
  "abv": { "pass": true, "found": "value on label or null" },
  "warning": { "pass": true, "notes": "what is missing or wrong if failed" }
}`;

export async function onRequestPost(context) {
  const { request, env } = context;

  const apiKey = env.OPENROUTER_API_KEY;
  if (!apiKey) {
    return new Response(JSON.stringify({ error: "OPENROUTER_API_KEY not configured" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }

  let formData;
  try {
    formData = await request.formData();
  } catch {
    return new Response(JSON.stringify({ error: "Invalid multipart form data" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const imageFile = formData.get("image");
  const brand = formData.get("brand");
  const abv = (formData.get("abv") || "").replace(/%$/, ""); // strip trailing % if present

  if (!imageFile || !brand || !abv) {
    return new Response(JSON.stringify({ error: "Missing required fields: image, brand, abv" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Convert image to base64 data URL
  const imageBytes = await imageFile.arrayBuffer();
  const base64 = arrayBufferToBase64(imageBytes);
  const mimeType = imageFile.type || "image/jpeg";
  const dataUrl = `data:${mimeType};base64,${base64}`;

  const prompt = PROMPT_TEMPLATE(brand, abv);

  const llmPayload = {
    model: MODEL,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image_url",
            image_url: { url: dataUrl },
          },
          {
            type: "text",
            text: prompt,
          },
        ],
      },
    ],
    max_tokens: 512,
  };

  let llmRes;
  try {
    llmRes = await fetch(OPENROUTER_URL, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ttb-label-verify.pages.dev",
        "X-Title": "TTB Label Verification",
      },
      body: JSON.stringify(llmPayload),
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: `Failed to reach OpenRouter: ${err.message}` }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    });
  }

  if (!llmRes.ok) {
    const errText = await llmRes.text();
    return new Response(JSON.stringify({ error: `OpenRouter error ${llmRes.status}: ${errText}` }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    });
  }

  const llmData = await llmRes.json();
  const content = llmData?.choices?.[0]?.message?.content ?? "";

  // Extract JSON from response (model may wrap it in markdown fences)
  let parsed;
  try {
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("No JSON object found in LLM response");
    parsed = JSON.parse(jsonMatch[0]);
  } catch (err) {
    return new Response(
      JSON.stringify({ error: `Failed to parse LLM response: ${err.message}`, raw: content }),
      { status: 502, headers: { "Content-Type": "application/json" } }
    );
  }

  return new Response(JSON.stringify(parsed), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "no-store",
    },
  });
}

function arrayBufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}
