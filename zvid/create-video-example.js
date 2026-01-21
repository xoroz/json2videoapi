import renderVideo from "zvid";

const project = {
  name: "basic-text-video",
  duration: 5,
  backgroundColor: "#1a1a2e",
  visuals: [
    {
      type: "TEXT",
      text: "Hello, Zvid!",
      position: "center-center",
      enterBegin: 0,
      enterEnd: 1,
      exitBegin: 4,
      exitEnd: 5,
      style: {
        fontSize: "64px",
        color: "#ffffff",
        textAlign: "center",
        fontWeight: "bold",
        letterSpacing: "2px",
      },
      enterAnimation: "fade",
      exitAnimation: "fade",
    },
  ],
};

async function createBasicVideo() {
  try {
    console.log("Creating basic video...");

    await renderVideo(project, "./output", (progress) => {
      console.log(`Progress: ${progress}%`);
    });

    console.log("Basic video created successfully!");
  } catch (error) {
    console.error("Error:", error.message);
  }
}

createBasicVideo();
