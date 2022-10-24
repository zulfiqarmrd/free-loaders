package com.example.mywear2.evaluation;

import android.util.Log;

public abstract class Task {
    private int id;

    public Task(int id) {
        this.id = id;
    }

    public int getId() {
        return this.id;
    }

    public String getInput() {
        return "";
    }

    public void runLocally() {
        Log.i("fle", "Starting task #" + this.getId());
        this.runLocallyInternal();
        Log.i("fle", "Completed task #" + this.getId());
    }

    public abstract void runLocallyInternal();
}
