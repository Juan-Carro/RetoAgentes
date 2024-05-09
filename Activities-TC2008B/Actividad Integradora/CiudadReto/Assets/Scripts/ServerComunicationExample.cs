/*
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using System;

public class ServerCommunicationExample : MonoBehaviour {
    public static event Action<List<CarTransform.CarData>> OnCarDataReceived;

    [Serializable]
    public class CarDataList {
        public List<CarTransform.CarData> cars;
    }
    
    
    
    private void UpdateCarData(CarDataList carDataList) {
        foreach (var carData in carDataList.cars) {
            if (!CheckIfCarExists(carData.id)) {
                CreateCar(carData);
            } else {
                UpdateCarPosition(carData);
            }
        }
    }

    private bool CheckIfCarExists(string carId) {
        foreach (var car in FindObjectsOfType<CarTransform>()) {
            if (car.id == carId) {
                return true;
            }
        }
        return false;
    }

    private void CreateCar(CarTransform.CarData carData) {
        GameObject carPrefab = "car"; // Asigna tu prefab de coche aquí.
        Vector3 position = new Vector3(carData.position[0], carData.position[1], carData.position[2]);
        GameObject newCar = Instantiate(carPrefab, position, Quaternion.identity);
        CarTransform carTransformScript = newCar.GetComponent<CarTransform>();
        carTransformScript.SetCarData(carData.id, position, carData.direction);
    }

    private IEnumerator Start() {
        string url = "http://127.0.0.1:8080/obtain_cars";
        
        while (true) {
            using (UnityWebRequest getRequest = UnityWebRequest.Get(url)) {
                yield return getRequest.SendWebRequest();

                if (getRequest.result == UnityWebRequest.Result.Success) {
                    CarDataList carDataList = JsonUtility.FromJson<CarDataList>(getRequest.downloadHandler.text);
                    OnCarDataReceived?.Invoke(carDataList.cars);
                    UpdateCarData(carDataList); // Llama a UpdateCarData aquí.
                } else {
                    Debug.Log("Error with server communication: " + getRequest.error);
                }
            }
            yield return new WaitForSeconds(1); 
        }
    }

}    */