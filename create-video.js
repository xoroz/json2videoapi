import renderVideo from "zvid";

// Define your video project
const project = {
  name: "hello-world",
  resolution: "hd", // 1280x720 - you can also use "full-hd", "squared", etc.
  duration: 5,
  visuals: [
    {
      type: "TEXT",
      text: "Hello, World!",
      position: "center-center",
      // enterStart: 0, // The default enterBegin is 0
      enterEnd: 1,
      exitBegin: 4,
      // exitEnd: 5, // The exitEnd is the project duration = 5
      style: {
        fontSize: "72px",
        fontFamily: "Roboto",
        textAlign: "center",
        fontWeight: "bold",
      },
      enterAnimation: "fade",
      exitAnimation: "fade",
    },
  ],
};

// Create the video
async function createVideo() {
  try {
    console.log("Starting video creation...");

    await renderVideo(project, "./output", (progress) => {
      console.log(`Progress: ${progress}%`);
    });

    console.log("Video created successfully! Check ./output/hello-world.mp4");
  } catch (error) {
    console.error("Error creating video:", error);
  }
}

createVideo();
