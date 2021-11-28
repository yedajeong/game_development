using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Vase : MonoBehaviour
{
    private Rigidbody vaseRigid;
    private Transform vaseTarget;
    private bool planeCollide;

    [SerializeField]
    private float vaseSpeed;

    void Start()
    {
        vaseRigid = GetComponent<Rigidbody>();
        planeCollide = false;
    }

    void OnTriggerEnter(Collider other)
    {
        if (other.tag == "Player")
        {
            vaseTarget = FindObjectOfType<PlayerController>().transform;
            gameObject.transform.LookAt(vaseTarget);
            vaseRigid.velocity = transform.forward * vaseSpeed;
            vaseRigid.isKinematic = false;
        }
    }

    void OnCollisionEnter(Collision other)
    {

        if (other.transform.tag == "Player" && !planeCollide)
        {
            PlayerController playerCon = other.transform.GetComponent<PlayerController>();
            playerCon.Die();
            Debug.Log("플레이어와 충돌했습니다");
        }

        else if (other.transform.tag == "Plane")
        {
            planeCollide = true;
            Debug.Log("바닥과 충돌했습니다.");
        }
    }
}
