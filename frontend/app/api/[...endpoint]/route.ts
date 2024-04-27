export async function POST(
  request: Request,
  { params }: { params: { endpoint: string[] } }
) {
  const formData = await request.formData();
  const backendResponse = await fetch(
    `${process.env.BACKEND_URL!}/${params.endpoint.join("/")}`,
    {
      method: "POST",
      body: formData as any,
      headers: {
        "API-Key": process.env.BACKEND_API_KEY!,
      },
    }
  );
  if (!backendResponse.ok) {
    return new Response("Failed to upload files to backend", { status: 500 });
  }

  const result = await backendResponse.json();

  return new Response(JSON.stringify(result), { status: 200 });
}

export async function GET(
  request: Request,
  { params }: { params: { endpoint: string[] } }
) {
  const backendResponse = await fetch(
    `${process.env.BACKEND_URL!}/${params.endpoint.join("/")}`,
    {
      method: "GET",
      headers: {
        "API-Key": process.env.BACKEND_API_KEY!,
      },
    }
  );

  if (!backendResponse.ok) {
    return new Response("Failed to fetch data from backend", { status: 500 });
  }

  const result = await backendResponse.json();

  return new Response(JSON.stringify(result), { status: 200 });
}
