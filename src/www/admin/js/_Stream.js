class Stream {
    async fetchStreamInfo() {
        try {
            const response = await fetch('/data/stream.json'); // Request data
            const data = await response.json();
            return data.stream; // Return the fetched stream data
        } catch (error) {
            console.error("Error fetching stream info:", error);
            return {};
        }
    }
}
export class StreamSingleton {
    static instance = null;
    streamInfo = {};

    static async getInstance() {
        if (!StreamSingleton.instance) {
            StreamSingleton.instance = new StreamSingleton();
            await StreamSingleton.instance.initializeStreamInfo();
        }
        return StreamSingleton.instance;
    }

    async initializeStreamInfo() {
        const stream = new Stream();
        this.streamInfo = await stream.fetchStreamInfo();
    }
}

 