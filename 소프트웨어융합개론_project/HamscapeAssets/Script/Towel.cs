using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Towel : MonoBehaviour
{
    private Rigidbody towelRigid;
    private Transform towelTarget;
    private bool planeCollide;

    [SerializeField]
    private float towelSpeed;

    void Start()
    {
        towelRigid = GetComponent<Rigidbody>();
        planeCollide = false;
    }

    void OnTriggerEnter(Collider other)
    {
        if (other.tag == "Player")
        {
            towelTarget = FindObjectOfType<PlayerController>().transform;
            gameObject.transform.LookAt(towelTarget);
            towelRigid.velocity = transform.forward * towelSpeed;
            towelRigid.isKinematic = false;
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
