using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class FloatingTextManager : MonoBehaviour
{
    public static FloatingTextManager instance;

    [SerializeField] GameObject prefab_FloatingText; // 복제할 원본 플로팅텍스트

    // Start is called before the first frame update
    void Start()
    {
        // 어디서든 FloatingTextManager를 참조할 수 있도록 자기자신을 인스턴스화
        instance = this; 
    }

    // 프리팹을 어디에 띄울지(coin의 position값 vector3로)
    public void CreateFloatingText(Vector3 position) 
    {
        // 프리팹 생성
        GameObject clone = Instantiate(prefab_FloatingText, position, prefab_FloatingText.transform.rotation);
        clone.transform.LookAt(Camera.main.transform.position);
    }
   
}
