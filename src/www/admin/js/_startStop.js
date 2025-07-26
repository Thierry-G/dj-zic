import { ALERT, H1, BG, ALERT_BORDER } from './_Colors.js';
import { StreamSingleton } from './_Stream.js';

export class StreamController {
    constructor() {
        this.eventStart = document.getElementById('eventStart');
        this.mode = 'pause';
        this.cmd = 'setMode';
        // Don't call initButtonState here - wait for StreamSingleton
    }

    async init() {
        // Initialize after StreamSingleton is ready
        const singleton = await StreamSingleton.getInstance();
        await this.initButtonState();
        return this;
    }

    async initButtonState() {
        const singleton = await StreamSingleton.getInstance();
        const streamInfo = singleton.streamInfo;
        
        // Set initial button text based on stream status
        switch (streamInfo['status']) {
            case 'start':
                this.eventStart.innerHTML = "Stoper le live Stream";
                this.mode = 'start';
                break;
            case 'pause':
            case 'stop':
            default:
                this.eventStart.innerHTML = "Démarrer le live Stream!";
                this.mode = 'pause';
                break;
        }
    }

    async getMode() {
        const singleton = await StreamSingleton.getInstance();
        const streamInfo = singleton.streamInfo;
        let state, url;

        switch (streamInfo['status']) {
            case 'start':
                this.eventStart.innerHTML = "Démarrer le live Stream!";
                state = 'pause';
                break;

            case 'pause':
            case 'stop':
            default:
                this.eventStart.innerHTML = "Stoper le live Stream";
                state = 'start';
                break;
        }

        url = `/admin/cmd.php?cmd=${encodeURIComponent(this.cmd)}&status=${encodeURIComponent(state)}`;
        
        try {
            const response = await fetch(url);
            const text = await response.text();
            streamInfo['status'] = state;
            console.log('Stream state updated:', state);
        } catch (error) {
            console.error('Error updating stream state:', error);
        }
    }
}
