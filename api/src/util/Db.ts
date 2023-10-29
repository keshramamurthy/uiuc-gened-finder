import { AsyncDatabase } from "promised-sqlite3";

export const DATABASE_PATH = "../sp24-courses.db"; // Change this to the database you saved to while scraping

export class DatabaseHandler {
    private static _instance: DatabaseHandler;
    private _database: AsyncDatabase;

    private constructor () {

    }

    public static getInstance(): DatabaseHandler {
        if (!DatabaseHandler._instance) {
            DatabaseHandler._instance = new DatabaseHandler();
        }

        return DatabaseHandler._instance;
    }

    public async getDb() {
        if (!this._database) {
            const db = await AsyncDatabase.open(DATABASE_PATH);
            this._database = db;
        }

        return this._database;
    }
}