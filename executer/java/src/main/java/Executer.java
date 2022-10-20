import org.eclipse.paho.client.mqttv3.*;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.UUID;

public class Executer {
    public static final String CONTROLLER_EXECUTER_TASK_EXECUTE_TOPIC = "ctrl-exec-task-execute";
    public static final String EXECUTER_ID = "0";

    public static void main(String[] args) {
        String publisherId = UUID.randomUUID().toString();
        try {
//            IMqttClient publisher = new MqttClient("tcp://localhost:1883",publisherId);

            MqttClient client = new MqttClient(
                    "tcp://localhost:1883", // serverURI in format:
                    // "protocol://name:port"
                    MqttClient.generateClientId(), // ClientId
                    new MemoryPersistence()); // Persistence

            MqttConnectOptions options = new MqttConnectOptions();
            options.setAutomaticReconnect(true);
            options.setCleanSession(true);
            options.setConnectionTimeout(10);
            client.connect(options);

            client.setCallback(new MqttCallback() {

                @Override
                // Called when the client lost the connection to the broker
                public void connectionLost(Throwable cause) {
                    System.out.println("client lost connection " + cause);
                }

                @Override
                public void messageArrived(String topic, MqttMessage message) {
                    String s = new String(message.getPayload(), StandardCharsets.UTF_8);
                    System.out.println(s);
                }

                @Override
                // Called when an outgoing publish is complete
                public void deliveryComplete(IMqttDeliveryToken token) {
                    System.out.println("delivery complete " + token);
                }
            });

            client.subscribe(CONTROLLER_EXECUTER_TASK_EXECUTE_TOPIC, 1);



        } catch (MqttException e) {
            e.printStackTrace();
        }

    }
}
