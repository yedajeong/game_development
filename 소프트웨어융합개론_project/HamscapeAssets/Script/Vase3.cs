using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Vase3 : MonoBehaviour
{
    private Rigidbody vase3Rigid;
    private Transform vaseTarget;
    private bool planeCollide;


    [SerializeField]
    private float vase3Speed;
    
    void Start()
    {
        vase3Rigid = GetComponent<Rigidbody>();
        planeCollide = false;
    }

    void OnTriggerEnter(Collider other)
    {
        if (other.tag == "Player")
        {
            vaseTarget = FindObjectOfType<PlayerController>().transform;
            gameObject.transform.LookAt(vaseTarget);
            vase3Rigid.velocity = transform.forward * vase3Speed;
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
