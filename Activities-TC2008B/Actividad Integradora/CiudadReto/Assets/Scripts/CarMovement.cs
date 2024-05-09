using System.Collections;
using System.Collections.Generic;
using Unity.PlasticSCM.Editor.WebApi;
using UnityEngine;

public class CarMovement : MonoBehaviour {
    public Camera cam;
    public float speed;
    public List<Transform> colliders;

    public int index = 0;
    public int points = 21; // FIXME: Update it
    
    private Transform m_transform;
    private Vector3 m_destinationPosition;
    
    // Start is called before the first frame update
    private void Start() {
        m_transform = GetComponent<Transform>();
        m_destinationPosition = m_transform.position;
    }

    // Update is called once per frame
    private void Update() {
        m_destinationPosition = colliders[index].position;  // --> Transform in index   
        
        if (SetDestination(m_destinationPosition)) {
            index++;

            if (index > points) {
                index = points;
            }

            if (index == points) {
                index = 0;
            }
        }
        
    }
    
    private bool SetDestination(Vector3 destinationPosition) {
        Vector3 currentPosition = m_transform.position;
        Vector3 displacementVector = m_destinationPosition - currentPosition;
        Vector3 targetDirection = Vector3.Normalize(displacementVector);  // Goal Direction
        Vector3 currentDirection = m_transform.forward;
        Vector3 direction = Vector3.RotateTowards(currentDirection, targetDirection, 5f * Time.deltaTime, 0);
        m_transform.rotation = Quaternion.LookRotation(direction); 
        
        m_transform.position += direction * speed * Time.deltaTime;
        
        if (displacementVector.magnitude < 0.1f) {
            return true;
        }
        
        return false;
    }
}