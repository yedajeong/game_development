using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Book : MonoBehaviour
{
    private Rigidbody bookRigid;
    private bool planeCollide;
   
    [SerializeField]
    private float bookSpeed;
    
    void Start()
    {
        bookRigid = GetComponent<Rigidbody>();
        planeCollide = false;
    }

    void OnTriggerEnter(Collider other)
    {
        if (other.tag == "Player")
        {
            transform.Translate(new Vector3(0, -1 , 0));
        }
    }
    
    void OnCollisionEnter(Collision other)
    {

        if (other.transform.tag == "Player" && planeCollide == false)
        {
            PlayerController playercon = other.transform.GetComponent<PlayerController>();
            playercon.Die();
            Debug.Log("플레이어와 충돌했습니다");
        }

        else if (other.transform.tag == "Plane")
        {
            planeCollide = true;
            Debug.Log("바닥과 충돌했습니다.");
        }
    }
}
