package com.example.mywear2.evaluation;

import android.util.Log;

public class ForLoopEvaluation extends Task {
    public ForLoopEvaluation(int id) {
        super(id);
    }

    @Override
    public void runLocally() {
        int sum = 0;
        for (int i = 0; i < this.getId() * 1000000 + 5000; i++) {
            sum += 1;
        }
    }
}
