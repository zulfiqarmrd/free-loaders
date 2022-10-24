package com.example.mywear2.evaluation;

public class MatrixEvaluation extends Task {
    private float[][] a;
    private float[][] b;

    private int width;
    private int height;

    private final int MAX_ID = 99;

    public MatrixEvaluation(int id) {
        super(id);

        this.width = (id - 50) + 2 + ((MAX_ID - id) / 2);
        this.height = (id - 50) + 2 + ((MAX_ID - id) / 2);
        this.a = new float[width][height];
        this.b = new float[width][height];
    }

    public String getInput() {
        String json = "{ a: [";
        for (int i = 0; i < this.width; i++) {
            json += "[";
            for (int j = 0; j < this.height; j++) {
                json += Float.toString(this.a[i][j]);
                if (j < this.height - 1) {
                    json += ", ";
                }
            }
            json += "]";
            if (i < this.width - 1) {
                json += ", ";
            }
        }
        json += "], b: ";

        for (int i = 0; i < this.width; i++) {
            json += "[";
            for (int j = 0; j < this.height; j++) {
                json += Float.toString(this.b[i][j]);
                if (j < this.height - 1) {
                    json += ", ";
                }
            }
            json += "]";
            if (i < this.width - 1) {
                json += ", ";
            }
        }

        json += "}";

        return json;
    }

    @Override
    public void runLocallyInternal() {
        int c[][] = new int[this.width][this.height];
        for (int y = 0; y < this.height; y++) {
            for (int x = 0; x < this.width; x++) {
                c[x][y] = 0;
                for (int i = 0; i < this.width; i++) {
                    c[x][y] += this.a[i][y] * this.b[x][i];
                }
            }
        }
    }
}
