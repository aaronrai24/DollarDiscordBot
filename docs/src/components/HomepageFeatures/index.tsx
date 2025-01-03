import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  imageSrc: string;  // Changed from Svg to imageSrc
  description: JSX.Element;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Easy to Use',
    imageSrc: require('@site/static/img/dollar_easy_to_use.png').default,
    description: (
      <>
        Dollar was designed from the ground up to seamlessly enhance your Discord experience,
        providing powerful tools for music, moderation, and automation—all while being easy to set up and use.
      </>
    ),
  },
  {
    title: 'Focus on What Matters',
    imageSrc: require('@site/static/img/dollar_focused.png').default,
    description: (
      <>
        Dollar lets you focus on enjoying your Discord server while it handles the heavy lifting.
        From managing music queues to automating tasks,
        Dollar keeps your server running smoothly—so you can focus on having fun.
      </>
    ),
  },
  {
    title: 'Powered by a Modern Tech Stack',
    imageSrc: require('@site/static/img/dollar_tech_stack.png').default,
    description: (
      <>
        Extend or customize Dollar's functionality using Python, Lavalink, and Docker. Dollar is designed to be flexible and scalable,
        allowing you to build on its features while maintaining seamless integration.
      </>
    ),
  },
];

function Feature({title, imageSrc, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <img className={styles.featureSvg} src={imageSrc} alt={title} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): JSX.Element {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}