package com.example.mywear2;

import android.opengl.Matrix;
import android.util.Log;

import com.example.mywear2.evaluation.ForLoopEvaluation;
import com.example.mywear2.evaluation.MatrixEvaluation;
import com.example.mywear2.evaluation.Task;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

import kotlin.random.Random;

public class FLEvaluation {

    private final String controllerAddress = "192.168.2.1:8001";
    URL submitUrl;

    ArrayList<Thread> threads;

    public FLEvaluation() throws MalformedURLException {
        this.submitUrl = new URL("http://" + this.controllerAddress + "/submit-task");
        this.threads = new ArrayList<>();
    }

    public void run() {
        Log.i("fle", "Starting evaluation.");

        // Randomize the ordering of tasks.
        ArrayList<Integer> taskIds = new ArrayList<>();
        ArrayList<Integer> taskOrdering = new ArrayList<>();
        for (int i = 0; i < 150; i++) {
            taskIds.add(i);
        }
        while (!taskIds.isEmpty()) {
            int idx = Random.Default.nextInt(taskIds.size());
            taskOrdering.add(taskIds.get(idx));
            taskIds.remove(idx);
        }

        for (int i = 0; i < 150; i++) {
            final int j = taskOrdering.get(i);
            Runnable r = new Runnable() {
                @Override
                public void run() {
                    Log.i("fle", "Running task #" + Integer.toString(j));

                    HttpURLConnection conn = null;
                    try {
                        conn = (HttpURLConnection) submitUrl.openConnection();
                    } catch (IOException e) {
                        Log.e("fle", "Could not open connection to controller: " + e.getMessage());
                        return;
                    }
                    conn.setDoOutput(true);
                    conn.setReadTimeout(999999);

                    // Pick a task.
                    Task evaluationTask = null;
                    if (j < 50) {
                        evaluationTask = new ForLoopEvaluation(j);
                    } else if (j < 100) {
                        evaluationTask = new MatrixEvaluation(j);
                    } else {
                        // Image classification.
                        return;
                    }

                    String body = evaluationTask.getInput();
                    try {
                        conn.getOutputStream().write(body.getBytes(StandardCharsets.UTF_8));
                        conn.getOutputStream().close();
                    } catch (IOException e) {
                        Log.e("fle", "I/O error: " + e.getMessage());
                        return;
                    }

                    // Look at the response.
                    try {
                        InputStream responseStream = conn.getErrorStream();
                        if (responseStream == null)
                            responseStream = conn.getInputStream();

                        BufferedReader reader = new BufferedReader(new InputStreamReader(responseStream, "UTF-8"));
                        StringBuffer responseBuffer = new StringBuffer();
                        String responseLine;
                        while ((responseLine = reader.readLine()) != null)
                            responseBuffer.append(responseLine);
                        reader.close();
                    } catch (IOException e) {
                        Log.e("fle", "I/O exception for task #" + j);
                        return;
                    }

                    Log.i("fle", "Task #" + j + " completed.");
                }
            };
            Thread taskThread = new Thread(r);
            taskThread.start();
            this.threads.add(taskThread);

            // Wait for .5 to 1 second.
            try {
                Thread.sleep(500 + (Random.Default.nextInt() % 500));
            } catch (InterruptedException e) {
                Log.e("fle", "Sleep interrupted.");
                return;
            }
        }

        // Wait for all to finish before returning.
        boolean allDone = false;
        while (!allDone) {
            try {
                Thread.sleep(473);
            } catch (InterruptedException e) {
                Log.e("fle", "Thread check sleep interrupted.");
                continue;
            }

            allDone = true;
            for (Thread t : this.threads) {
                allDone = allDone && t.isAlive();
                if (!allDone) { break; }
            }
        }

        Log.i("fle", "Done running all tasks.");
    }
}