using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// This script is responsible for smoothly following the point cloud figure.
/// The RenderPointCloud script determines the centroid and sends it to this script.
/// We smooth the movement and rotation according to user given parameters.
/// Users can also drive the camera in real time, relative to the centroid.
/// </summary>

public class FollowPointCloudCamera : MonoBehaviour
{

    [Header("Camera Control Variables")]
    

    //camera movement variables
    //can edit in editor
    [SerializeField]
    private bool lookAtCentroid = true;


    [SerializeField]
    private float manualCameraSpeed = .1f;

    [SerializeField]
    private float manualRotationSpeed = .1f;

    [SerializeField]
    private float baseCameraPositionXOffset = 0f;

    [SerializeField]
    private float baseCameraPositionYOffest = 0f;

    [SerializeField]
    private float baseCameraPositionZOffset = 0f;

    [SerializeField]
    private float lookAtHeadOffset = 1f;
   
    [SerializeField]
    private float cameraSmoothTime = .3f;

    [SerializeField]
    private float lookAtSmoothTime = .3f;



    //camera movement variables
    //can not edit in editor
    private float userInputXOffset = 0;

    private float userInputYOffset = 0;

    private float userInputZOffset = 0;

    private float userRotationXOffset = 0;

    private float userRotationYOffset = 0;

    private float userRotationZOffset = 0;

    private Vector3 newCameraPosition = Vector3.zero;

    private Quaternion newCameraAngle;

    private Vector3 centroid = Vector3.zero;

    private Vector3 cameraSmoothVelocity = Vector3.zero;

    private Vector3 lookAtSmoothVelocity = Vector3.zero;

    private Vector3 oldLookat = Vector3.zero;
    // Start is called before the first frame update
    void Awake()
    {
        
    }

    public void UpdateCameraPosition(Vector3 centroid, Vector3 lookAt){

        // //add user offset values to centroid offset, that way we don't constantly look at the center of the dancer.
        newCameraPosition.x = centroid.x+baseCameraPositionXOffset+userInputXOffset;
        newCameraPosition.y = centroid.y+baseCameraPositionYOffest+userInputYOffset;
        newCameraPosition.z = centroid.z+baseCameraPositionZOffset+userInputZOffset;
        
        //move the camera each frame, but apply smoothing
        transform.localPosition = Vector3.SmoothDamp(transform.localPosition, newCameraPosition, ref cameraSmoothVelocity, cameraSmoothTime);

        Vector3 head = new Vector3(lookAt.x, lookAt.y+lookAtHeadOffset,lookAt.z);

        if(lookAtCentroid){

            Vector3 newLookat = Vector3.SmoothDamp(oldLookat, head, ref lookAtSmoothVelocity, lookAtSmoothTime);
            transform.LookAt(newLookat);
            oldLookat = newLookat;

        } else {

            Vector3 newAngle = new Vector3(userRotationXOffset,userRotationYOffset,userRotationZOffset);
            newCameraAngle.eulerAngles = newAngle;
            
            //move the camera each frame, but apply smoothing
            transform.localPosition = Vector3.SmoothDamp(transform.localPosition, newCameraPosition, ref cameraSmoothVelocity, cameraSmoothTime);
            transform.rotation = Quaternion.Lerp(transform.rotation, newCameraAngle, Time.time * lookAtSmoothTime);
        }
        

    }

    // Update is called once per frame
    void Update(){


        if (Input.GetKey("up"))
        {
            userRotationXOffset-=manualRotationSpeed;
        }

        if (Input.GetKey("down"))
        {
            userRotationXOffset+=manualRotationSpeed;
        }

        if (Input.GetKey("left"))
        {
            userRotationYOffset-=manualRotationSpeed;
        }

        if (Input.GetKey("right"))
        {
            userRotationYOffset+=manualRotationSpeed;
        }

        if (Input.GetKey("q"))
        {
            userInputYOffset-=manualCameraSpeed;
        }

        if (Input.GetKey("e"))
        {
            userInputYOffset+=manualCameraSpeed;
        }

        if (Input.GetKey("a"))
        {
            userInputXOffset-=manualCameraSpeed;
        }

        if (Input.GetKey("d"))
        {
            userInputXOffset +=manualCameraSpeed;
        }

        if (Input.GetKey("w"))
        {
            userInputZOffset+=manualCameraSpeed;
        }

        if (Input.GetKey("s"))
        {
            userInputZOffset -=manualCameraSpeed;
        }


        
    }
}
