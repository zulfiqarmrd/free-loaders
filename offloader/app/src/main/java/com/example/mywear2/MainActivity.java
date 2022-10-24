package com.example.mywear2;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;

import com.google.android.material.snackbar.Snackbar;

import androidx.appcompat.app.AppCompatActivity;

import android.os.BatteryManager;
import android.os.Handler;
import android.util.Log;
import android.view.View;

import androidx.navigation.NavController;
import androidx.navigation.Navigation;
import androidx.navigation.ui.AppBarConfiguration;
import androidx.navigation.ui.NavigationUI;

import com.example.mywear2.databinding.ActivityMainBinding;

import android.view.Menu;
import android.view.MenuItem;
import android.widget.Button;
import android.widget.TextView;

import java.net.MalformedURLException;

public class MainActivity extends AppCompatActivity {

    private AppBarConfiguration appBarConfiguration;
    private ActivityMainBinding binding;
    private Handler updateHandler;
    private Runnable updateStats;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        binding = ActivityMainBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        setSupportActionBar(binding.toolbar);

        NavController navController = Navigation.findNavController(this, R.id.nav_host_fragment_content_main);
        appBarConfiguration = new AppBarConfiguration.Builder(navController.getGraph()).build();
        NavigationUI.setupActionBarWithNavController(this, navController, appBarConfiguration);

        this.updateHandler = new Handler();
        this.updateStats = () -> {
            BatteryManager batteryManager = (BatteryManager) getApplicationContext().getSystemService(BATTERY_SERVICE);
            int currentCapacity = batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CHARGE_COUNTER);
            TextView tv = findViewById(R.id.textview_capacity);
            tv.setText(Integer.toString(currentCapacity));
            // Periodic update.
            updateHandler.postDelayed(updateStats, 2000);
        };
        this.updateHandler.postDelayed(this.updateStats, 0);

        Button evalButton = findViewById(R.id.evalButton);
        this.configureEvaluationButton(evalButton);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @Override
    public boolean onSupportNavigateUp() {
        NavController navController = Navigation.findNavController(this, R.id.nav_host_fragment_content_main);
        return NavigationUI.navigateUp(navController, appBarConfiguration)
                || super.onSupportNavigateUp();
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        this.updateHandler.removeCallbacks(this.updateStats);
    }

    private void configureEvaluationButton(Button targetButton) {
        targetButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // Change the button to signal evaluation is running.
                targetButton.setClickable(false);
                targetButton.setBackgroundColor(getColor(R.color.grey));
                targetButton.setText("Running");

                Runnable evaluationRunnable = new Runnable() {
                    @Override
                    public void run() {
                        try {
                            FLEvaluation fle = new FLEvaluation();
                            fle.run();
                        } catch (MalformedURLException e) {
                            Log.e("fle", "Cannot start evaluation (bad controller URL).");
                        }
                        targetButton.setText("Start");
                        targetButton.setClickable(true);
                    }
                };
                Thread t = new Thread(evaluationRunnable);
                t.start();
            }
        });
    }
}