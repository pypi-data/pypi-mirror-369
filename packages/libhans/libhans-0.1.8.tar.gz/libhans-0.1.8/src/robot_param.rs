use std::f64::consts::FRAC_PI_2;

pub const HANS_VERSION: &str = "0.1.0";
pub const HANS_DOF: usize = 6;

pub const ROPLAT_ASCII: &str = r#"
   #####     #####     ##### 
  #     #   #     #   #     #
  #     #   #     #   #     #
  #     #   #     #   #     # 
   #####    #     #    ##### 
  #   #     #     #   #      
  #    #    #     #   #      
  #     #    #####    #      
"#;

pub const HANS_ASCII: &str = r#"
  #     #    ###     #     #   ######
  #     #   #   #    ##    #  #      
  #     #  #     #   # #   #  #      
  #######  #######   #  #  #   ##### 
  #     #  #     #   #   # #        #
  #     #  #     #   #    ##        #
  #     #  #     #   #     #  ###### 
"#;

pub const HANS_ROBOT_MIN_JOINTS: [f64; HANS_DOF] = [-360.; HANS_DOF];
pub const HANS_ROBOT_MAX_JOINTS: [f64; HANS_DOF] = [360.; HANS_DOF];
pub const HANS_ROBOT_MAX_LOAD: f64 = 30.0;
pub const HANS_ROBOT_JOINT_VEL: [f64; HANS_DOF] = [120., 120., 120., 180., 180., 180.];
pub const HANS_ROBOT_JOINT_ACC: [f64; HANS_DOF] = [2.5; HANS_DOF];
pub const HANS_ROBOT_MAX_CARTESIAN_VEL: f64 = 3.7;
pub const HANS_ROBOT_MAX_CARTESIAN_ACC: f64 = 2.0;

pub const HANS_ROBOT_DH: [[f64; 4]; HANS_DOF] = [
    [0.0, 0.1857, 0.0, FRAC_PI_2],
    [0.0, 0.264, -0.85, 0.0],
    [0.0, 0.2065, -0.7915, 0.0],
    [0.0, 0.1585, 0.0, FRAC_PI_2],
    [0.0, 0.1585, 0.0, FRAC_PI_2],
    [0.0, 0.1345, 0.0, 0.0],
];
