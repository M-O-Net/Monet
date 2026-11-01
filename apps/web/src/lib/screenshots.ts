export const MAX_SCREENSHOT_BYTES = 1_000_000;
const MAX_SIDE = 1920;
const MIN_SIDE = 400;
const JPEG_QUALITY = 0.85;

export interface EncodedScreenshot {
  media_type: "image/jpeg";
  data: string;
  preview: string;
}

export function fitWithin(
  width: number,
  height: number,
  maxSide: number,
): { width: number; height: number } {
  const scale = Math.min(1, maxSide / Math.max(width, height));
  return {
    width: Math.max(1, Math.round(width * scale)),
    height: Math.max(1, Math.round(height * scale)),
  };
}

export function readAsDataUrl(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === "string") resolve(reader.result);
      else reject(new Error("Could not read the image."));
    };
    reader.onerror = () => {
      reject(new Error("Could not read the image."));
    };
    reader.readAsDataURL(blob);
  });
}

function encodeJpeg(bitmap: ImageBitmap, maxSide: number): Promise<Blob> {
  const { width, height } = fitWithin(bitmap.width, bitmap.height, maxSide);
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext("2d");
  if (context === null) return Promise.reject(new Error("This browser cannot shrink images."));
  context.fillStyle = "#ffffff";
  context.fillRect(0, 0, width, height);
  context.drawImage(bitmap, 0, 0, width, height);
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        if (blob === null) reject(new Error("Could not encode the image."));
        else resolve(blob);
      },
      "image/jpeg",
      JPEG_QUALITY,
    );
  });
}

export async function shrinkScreenshot(image: Blob): Promise<EncodedScreenshot> {
  const bitmap = await createImageBitmap(image);
  try {
    let side = MAX_SIDE;
    let blob = await encodeJpeg(bitmap, side);
    while (blob.size > MAX_SCREENSHOT_BYTES && side > MIN_SIDE) {
      side = Math.round(side * 0.75);
      blob = await encodeJpeg(bitmap, side);
    }
    const preview = await readAsDataUrl(blob);
    return { media_type: "image/jpeg", data: preview.slice(preview.indexOf(",") + 1), preview };
  } finally {
    bitmap.close();
  }
}
