import { DatabaseHandler } from "./Db";

export class Logger {
    private static _instance: Logger;

    private constructor() {

    }

    public static getInstance(): Logger {
        if (!Logger._instance) {
            Logger._instance = new Logger();
        }

        return Logger._instance;
    }

    public async logInfo(d: LogData) {
        const db = await DatabaseHandler.getInstance().getDb();
        await db.run("CREATE TABLE IF NOT EXISTS log(date, type, data)");
        db.run("INSERT INTO log (date, type, data) VALUES (?,?,?)", d.date.toUTCString(), JSON.stringify(d.data), d.type);
    }
}

export type LogData = {
    date: Date;
    data: object;
    type: EventType;
}

export type EventType = "SUBMIT" | "ERR" | "SEARCH" | "VISIT";