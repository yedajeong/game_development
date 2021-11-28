using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Pillow : MonoBehaviour
{
    private Rigidbody pillowRigid;
    private Transform pillowTarget;
    private bool planeCollide;
    private float pillowSpeed = 8f;

    void Start()
    {
        pillowRigid = GetComponent<Rigidbody>();
        planeCollide = false;
    }

    void OnTriggerEnter(Collider other)
    {
        if (other.tag == "Player")
        {
            pillowTarget = FindObjectOfType<PlayerController>().transform;
            gameObject.transform.LookAt(pillowTarget);
            pillowRigid.velocity = transform.forward * pillowSpeed;
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
