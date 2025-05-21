// Name Agent: Suggest a creative dish name using a free Hugging Face model
export async function suggestNameLLM({ mood, weather, base, protein, sauce }) {
  const prompt = `Suggest a creative, catchy, and appetizing dish name for a customer who is feeling ${mood}, the weather is ${weather}, and they chose ${base} with ${protein} and ${sauce}.`;
  const response = await fetch('https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ inputs: prompt })
  });
  const data = await response.json();
  // The model may return an array or object depending on the endpoint
  const text = Array.isArray(data) ? data[0]?.generated_text : data?.generated_text;
  return text?.replace(prompt, '').trim() || 'Your Special Dish';
}