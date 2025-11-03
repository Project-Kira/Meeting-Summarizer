// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Process Audio API - MAIN FUNCTION
 * 
 * Sends audio to backend and gets transcription + summary back
 * No sessionId needed - simple one-step process
 * 
 * How it works:
 * 1. Send recorded audio file to backend
 * 2. Backend uses Whisper AI to transcribe (speech → text)
 * 3. Backend uses Mistral AI to summarize (text → summary)
 * 4. Backend returns both transcription and summary
 * 
 * @param {Blob} audioBlob - Recorded audio from browser microphone
 * @returns {Object} { success: true/false, data: { transcription, summary } }
 * 
 * Example response:
 * {
 *   success: true,
 *   data: {
 *     transcription: "Hello everyone, today we discussed the project...",
 *     summary: "Key Points:\n- Project timeline\n- Team assignments\n- Next steps"
 *   }
 * }
 */
export const processAudioAPI = async (audioBlob) => {
	try {
		console.log('📤 processAudioAPI called');
		console.log('   Audio size:', audioBlob.size, 'bytes');
		console.log('   Audio type:', audioBlob.type);

		// Prepare audio file to send
		const formData = new FormData();
		formData.append('file', audioBlob, 'meeting.wav');
		console.log('   FormData created with audio file');

		const url = `${API_BASE_URL}/api/process`;
		console.log('   Sending POST request to:', url);

		// Send to backend
		const response = await fetch(url, {
			method: 'POST',
			body: formData,
		});

		console.log('   Response status:', response.status, response.statusText);

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}

		// Get transcription and summary from backend
		const data = await response.json();
		console.log('   Response data received:');
		console.log('   - Has transcription:', !!data.transcription);
		console.log('   - Has summary:', !!data.summary);
		console.log('   - Transcription length:', data.transcription?.length || 0);
		console.log('   - Summary length:', data.summary?.length || 0);

		return { success: true, data };
	} catch (error) {
		console.error('❌ Process audio API error:', error);
		console.error('   Error details:', error.message);
		return { success: false, error: error.message };
	}
};

/**
 * Health Check API (Optional)
 * 
 * Checks if backend is running
 */
export const healthCheckAPI = async () => {
	try {
		const response = await fetch(`${API_BASE_URL}/api/health`, {
			method: 'GET',
		});

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}

		const data = await response.json();
		return { success: true, data };
	} catch (error) {
		console.error('Health check API error:', error);
		return { success: false, error: error.message };
	}
};
