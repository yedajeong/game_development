using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayerController : MonoBehaviour
{
    public string currentMap; //맵이 이동되면 맵의 이름 저장
    public Rigidbody playerRigidbody; //이동에 사용할 리지드바디 컴포넌트

    [SerializeField]
    private float speed; //이동속력

    [SerializeField]
    private float jumpForce; //점프힘
    private CapsuleCollider playerCollider;
    private bool isGround = true;

    [SerializeField]
    private float lookSensitivity; //회전&카메라 민감도

    [SerializeField]
    private float cameraRotationLimit; //최대 회전각
    private float currentCameraRotationX; //현재 카메라 회전

    [SerializeField]
    private Camera theCamera; 
    

    void Start() 
    {
        DontDestroyOnLoad(this.gameObject);
        playerRigidbody = GetComponent<Rigidbody>();
        playerCollider = GetComponent<CapsuleCollider>();
    }

    void Update()
    {
        PlayerJump();
        PlayerMove();
        CameraRotation();
        PlayerRotation();
    }

    private void PlayerMove()
    {
        float _moveDirX = Input.GetAxis("Horizontal");
        float _moveDirZ = Input.GetAxis("Vertical");

        Vector3 _moveHorizontal = transform.right * _moveDirX;
        Vector3 _moveVertical = transform.forward * _moveDirZ;

        Vector3 _velocity = (_moveHorizontal + _moveVertical).normalized * speed;

        playerRigidbody.MovePosition(transform.position + _velocity * Time.deltaTime);
    }

    /*private void IsGround()
    {
        isGround = Physics.Raycast(transform.position, Vector3.down, playerCollider.bounds.extents.y + 0, 1f);
    }*/

    private void PlayerJump()
    {
        isGround = Physics.Raycast(transform.position, Vector3.down, playerCollider.bounds.extents.y + 0.1f);

        if (Input.GetKeyDown(KeyCode.Space) && isGround == true)
        {
            SoundManager.instance.PlaySE("jump");
            playerRigidbody.velocity = transform.up * jumpForce;
        }
    }
    private void PlayerRotation()
    {
        float yRotation = Input.GetAxisRaw("Mouse X");
        Vector3 characterRotationY = new Vector3(0f, yRotation, 0f) * lookSensitivity; //오일러 값
        playerRigidbody.MoveRotation(playerRigidbody.rotation * Quaternion.Euler(characterRotationY)); //쿼터니언 값으로 변환 (MoveRotation은 쿼너티언 값을 쓴다...?)
    }
    private void CameraRotation()
    {
        float _xRotation = Input.GetAxisRaw("Mouse Y");
        float _cameraRotationX = _xRotation * lookSensitivity;

        currentCameraRotationX -= _cameraRotationX;
        currentCameraRotationX = Mathf.Clamp(currentCameraRotationX, -cameraRotationLimit, cameraRotationLimit);

        theCamera.transform.localEulerAngles = new Vector3(currentCameraRotationX, 0f, 0f);
    }

    public void Die()
    {
        SoundManager.instance.PlaySE("hit");
        playerRigidbody.constraints = RigidbodyConstraints.FreezeAll;
        GameManager gameManager = FindObjectOfType<GameManager>();
        gameManager.GameOver();
    }
}