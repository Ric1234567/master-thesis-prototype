export class Util {
    async fetchFromBackend(method: string, route: string): Promise<string> {
        const response = await fetch('http://localhost:5000/' + route, {
            method: method,
            headers: {
                Accept: 'application/json'
            }
        });
        if (!response.ok) {
            throw new Error(`HttpError: ${response.status}!`);
        }
        return await response.json();
    }
}