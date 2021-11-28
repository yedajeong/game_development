using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Chair : MonoBehaviour
{
    private Rigidbody chairRigid;
    [SerializeField]

    void Start()
    {
        chairRigid = GetComponent<Rigidbody>();
    }

    void OnTriggerStay(Collider other)
    {
        if (other.tag == "Player")
        {
            transform.Rotate(new Vector3(0, 0, 200) * Time.deltaTime * 0.5f);
        }
    }

}
