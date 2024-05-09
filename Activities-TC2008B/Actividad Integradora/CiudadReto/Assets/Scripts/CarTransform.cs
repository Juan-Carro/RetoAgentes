/*
using System.Collections;
using System.Collections.Generic;
using Unity.PlasticSCM.Editor.WebApi;
using UnityEngine;

public class CarTransform : MonoBehaviour {
    public string id;
    public Vector3 targetPosition;
    public Quaternion targetRotation;

    [System.Serializable]
    public class CarData {
        public int id; 
        public List<int> position;
        public string direction;
    }
    
    public float speed;
    public Transform carTransform;
    
    public void SetCarData(string carId, Vector3 position, string direction) {
        this.id = carId;

        // Establecer la posición inicial del coche
        this.targetPosition = position;
        this.transform.position = position; // Esto mueve el coche a la posición inicial

        // Convertir la dirección en una rotación y establecerla
        this.targetRotation = DirectionToQuaternion(direction);
        this.transform.rotation = targetRotation; // Esto orienta el coche en la dirección inicial
    }

    private void OnEnable() {
        ServerCommunicationExample.OnCarDataReceived += UpdateCarPosition;
    }

    private void OnDisable() {
        ServerCommunicationExample.OnCarDataReceived -= UpdateCarPosition;
    }

    private void UpdateCarPosition(List<CarData> carDataList) {
        foreach (var carData in carDataList) {
            Vector3 newPosition = new Vector3(carData.position[0], carData.position[1], carData.position[2]);
            carTransform.position = newPosition;

            Quaternion newRotation = DirectionToQuaternion(carData.direction);
            carTransform.rotation = newRotation;
        }
    }

    private Quaternion DirectionToQuaternion(string direction) {
        switch (direction) {
            case "N":
                return Quaternion.Euler(0, 0, 0);
            case "E":
                return Quaternion.Euler(0, 90, 0);
            case "S":
                return Quaternion.Euler(0, 180, 0);
            case "W":
                return Quaternion.Euler(0, 270, 0);
            case "NE":
                return Quaternion.Euler(0, 45, 0);
            case "SE":
                return Quaternion.Euler(0, 135, 0);
            case "SW":
                return Quaternion.Euler(0, 225, 0);
            case "NW":
                return Quaternion.Euler(0, 315, 0);
            default:
                return Quaternion.identity;
        }
    }
}
*/
